from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommand,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import CommandStart
import asyncio
import requests

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN, CHANNEL_ID, API_BASE

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


class QuizFlow(StatesGroup):
    waiting_profile = State()
    waiting_category = State()
    waiting_quiz = State()


async def check_sub(user_id: int) -> bool:
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in ["member", "administrator", "creator"]


def back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True,
    )


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🏛 <b>Registon Imtihon Markazi</b>\n\n"
        "📚 Online Quiz Platform\n\n"
        "Iltimos ismingiz va email’ingizni bitta xabarga yozing:\n"
        "<b>Name</b>, <b>email@example.com</b>\n\n"
        "Misol: Ali, ali@gmail.com"
    )
    await state.set_state(QuizFlow.waiting_profile)


@dp.message(QuizFlow.waiting_profile)
async def profile_handler(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if "," not in text:
        await message.answer("Format xato. Misol: Ali, ali@gmail.com")
        return

    name, email = [p.strip() for p in text.split(",", 1)]

    # Upsert minimal
    r = requests.post(f"{API_BASE}/students", json={"name": name, "email": email})
    if r.status_code >= 300 and r.status_code != 400:
        await message.answer("Student ro‘yxatdan o‘tishda xato yuz berdi.")
        return

    await state.update_data(student_name=name, student_email=email)

    cats = requests.get(f"{API_BASE}/categories")
    cats.raise_for_status()
    data = cats.json() or []

    if not data:
        await message.answer("Hozircha kategoriya yo‘q.")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=d["name"])] for d in data[:20]],
        resize_keyboard=True,
    )

    await message.answer("Kategoriya tanlang:", reply_markup=kb)
    await state.set_state(QuizFlow.waiting_category)


@dp.message(QuizFlow.waiting_category)
async def category_handler(message: Message, state: FSMContext):
    if (message.text or "").strip() == "⬅️ Orqaga":
        await state.clear()
        await message.answer("Ism va email yuboring: Name, email")
        await state.set_state(QuizFlow.waiting_profile)
        return

    category_name = (message.text or "").strip()

    cats = requests.get(f"{API_BASE}/categories")
    cats.raise_for_status()
    cat = next((c for c in cats.json() if c.get("name") == category_name), None)
    if not cat:
        await message.answer("Kategoriya topilmadi.")
        return

    quizzes = requests.get(f"{API_BASE}/quizzes", params={"category_id": cat["id"]})
    quizzes.raise_for_status()
    qlist = quizzes.json() or []

    if not qlist:
        await message.answer("Ushbu kategoriya ostida quiz yo‘q.")
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=q["question"][:40])] for q in qlist[:10]],
        resize_keyboard=True,
    )

    await state.update_data(category_id=int(cat["id"]), quizzes=qlist)
    await message.answer("Quiz tanlang:", reply_markup=kb)
    await state.set_state(QuizFlow.waiting_quiz)


@dp.message(QuizFlow.waiting_quiz)
async def quiz_handler(message: Message, state: FSMContext):
    if (message.text or "").strip() == "⬅️ Orqaga":
        await state.set_state(QuizFlow.waiting_category)
        await message.answer("Kategoriya tanlang:")
        return

    data = await state.get_data()
    qlist = data.get("quizzes") or []

    picked = None
    for q in qlist:
        if (q.get("question") or "").startswith(message.text or ""):
            picked = q
            break
    if not picked:
        picked = qlist[0]

    quiz_id = int(picked["id"])

    correct_1to4 = int(picked["correct"])

    # Telegram poll UI: aiogram 0..3 uchun correct_option_id talab qiladi
    correct_option_id = correct_1to4 - 1

    await bot.send_poll(
        chat_id=message.chat.id,
        question=picked["question"],
        options=[
            picked["option1"],
            picked["option2"],
            picked["option3"],
            picked["option4"],
        ],
        type="quiz",
        correct_option_id=correct_option_id,
    )

    await state.update_data(current_quiz_id=quiz_id)


@dp.poll_answer()
async def poll_answer_handler(poll_answer, state: FSMContext):
    selected = getattr(poll_answer, "option_ids", None)
    if not selected:
        selected = getattr(poll_answer, "option_id", None)

    if isinstance(selected, list) and selected:
        selected_option_0to3 = int(selected[0])
    elif selected is not None:
        selected_option_0to3 = int(selected)
    else:
        return

    # Telegram option index 0..3 -> backend expects 1..4
    selected_option_id_1to4 = selected_option_0to3 + 1

    data = await state.get_data()
    quiz_id = data.get("current_quiz_id")
    student_email = data.get("student_email")
    student_name = data.get("student_name")

    if not (quiz_id and student_email and student_name):
        return

    r = requests.post(
        f"{API_BASE}/quiz-attempt/submit",
        json={
            "quiz_id": int(quiz_id),
            "student_name": student_name,
            "student_email": student_email,
            "selected_option_id": int(selected_option_id_1to4),
        },
        timeout=20,
    )

    if r.status_code >= 300:
        return

    resp = r.json()
    correct = bool(resp.get("correct"))
    score = int(resp.get("score", 0))

    text = "✅ To‘g‘ri!" if correct else "❌ Noto‘g‘ri!"
    await poll_answer.bot.send_message(
        poll_answer.user.id,
        f"{text}\nHozirgi ball: <b>{score}</b>",
    )


async def main():
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start"),
            BotCommand(command="admin", description="Admin Panel"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

