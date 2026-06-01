from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommand,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.filters import CommandStart, Command
import asyncio
import requests
import json
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN, CHANNEL_ID, API_BASE

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


class QuizState(StatesGroup):
    """State machine for quiz flow"""
    waiting_email = State()
    selecting_category = State()
    selecting_quiz = State()
    answering_question = State()
    quiz_complete = State()


class UserSession:
    """Track user quiz session"""
    def __init__(self):
        self.student_id = None
        self.student_email = None
        self.student_name = None
        self.attempt_id = None
        self.quiz_id = None
        self.current_question_index = 0
        self.questions = []
        self.started_at = None

# Store user sessions
user_sessions = {}


def get_user_session(user_id: int) -> UserSession:
    """Get or create user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    return user_sessions[user_id]


async def check_sub(user_id: int) -> bool:
    """Check if user is subscribed to channel"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return True  # If error, allow access


def main_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Quizlar")],
            [KeyboardButton(text="🏆 Leaderboard"), KeyboardButton(text="👤 Profil")],
            [KeyboardButton(text="❓ Yordam"), KeyboardButton(text="⚙️ Sozlamalar")],
        ],
        resize_keyboard=True,
    )


def back_keyboard() -> ReplyKeyboardMarkup:
    """Back button keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
        resize_keyboard=True,
    )


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    user_id = message.from_user.id
    await state.clear()
    
    # Check subscription
    is_subscribed = await check_sub(user_id)
    if not is_subscribed:
        await message.answer(
            "🚫 Iltimos, kanalni follow qiling:\n\n"
            f"@{CHANNEL_ID}\n\n"
            "Keyin /start bosing."
        )
        return
    
    await message.answer(
        "🏛 <b>REGISTON Imtihon Markazi</b>\n\n"
        "📚 Online Quiz Platform\n\n"
        "<b>Assaloma-aleykum!</b> Xush kelibsiz! 👋\n\n"
        "Iltimos ism va email'ingizni kiriting:\n"
        "<b>Ism Email</b> formatida\n\n"
        "Misol: <code>Ali ali@gmail.com</code>",
        reply_markup=back_keyboard(),
    )
    await state.set_state(QuizState.waiting_email)


@dp.message(QuizState.waiting_email)
async def email_handler(message: Message, state: FSMContext):
    """Handle user email input"""
    if (message.text or "").strip() == "⬅️ Orqaga":
        await state.clear()
        await message.answer("Menu:", reply_markup=main_keyboard())
        return
    
    text = (message.text or "").strip()
    parts = text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Format xato. Misol: <code>Ali ali@gmail.com</code>")
        return
    
    name = parts[0]
    email = " ".join(parts[1:])
    
    # Validate email
    if "@" not in email:
        await message.answer("❌ Email to'g'ri emas. @  belgisi bo'lishi kerak.")
        return
    
    try:
        # Register/get student
        response = requests.post(
            f"{API_BASE}/students",
            json={"name": name, "email": email, "score": 0},
            timeout=10
        )
        
        if response.status_code == 400:
            # Student already exists
            student_data = requests.get(
                f"{API_BASE}/students",
                timeout=10
            ).json()
            student = next((s for s in student_data if s["email"] == email), None)
        else:
            student = response.json()
        
        if not student:
            await message.answer("❌ Xato yuz berdi. Iltimos qayta urinib ko'ring.")
            return
        
        session = get_user_session(message.from_user.id)
        session.student_id = student["id"]
        session.student_email = email
        session.student_name = name
        
        await message.answer(
            f"✅ Salom, <b>{name}</b>!\n\n"
            "Kategoriya tanlang:",
            reply_markup=await get_categories_keyboard(),
        )
        await state.set_state(QuizState.selecting_category)
        
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ Server bilan aloqa xato. Iltimos qayta urinib ko'ring.")


async def get_categories_keyboard() -> ReplyKeyboardMarkup:
    """Get categories as keyboard"""
    try:
        response = requests.get(f"{API_BASE}/categories", timeout=10)
        if response.status_code != 200:
            return back_keyboard()
        
        categories = response.json()
        if not categories:
            return back_keyboard()
        
        buttons = [
            [KeyboardButton(text=f"📖 {cat['name']}")] 
            for cat in categories[:10]
        ]
        buttons.append([KeyboardButton(text="⬅️ Orqaga")])
        
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    except:
        return back_keyboard()


@dp.message(QuizState.selecting_category)
async def category_handler(message: Message, state: FSMContext):
    """Handle category selection"""
    if (message.text or "").strip() == "⬅️ Orqaga":
        await state.clear()
        await message.answer("Menu:", reply_markup=main_keyboard())
        return
    
    category_name = (message.text or "").strip().replace("📖 ", "")
    
    try:
        # Get categories
        response = requests.get(f"{API_BASE}/categories", timeout=10)
        categories = response.json()
        category = next((c for c in categories if c["name"] == category_name), None)
        
        if not category:
            await message.answer("❌ Kategoriya topilmadi.")
            return
        
        # Get quizzes for this category
        response = requests.get(
            f"{API_BASE}/v2/quizzes",
            params={"category_id": category["id"], "status": "published"},
            timeout=10
        )
        
        if response.status_code != 200:
            quizzes = []
        else:
            quizzes = response.json()
        
        if not quizzes:
            await message.answer(
                f"📭 <b>{category_name}</b> kategoriyasida hali quiz yo'q.\n\n"
                "Boshqa kategoriya tanlang:",
                reply_markup=await get_categories_keyboard(),
            )
            return
        
        session = get_user_session(message.from_user.id)
        
        # Create keyboard with quizzes
        buttons = [
            [KeyboardButton(text=f"📝 {quiz['title']}")] 
            for quiz in quizzes[:10]
        ]
        buttons.append([KeyboardButton(text="⬅️ Orqaga")])
        
        keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        
        await message.answer(
            f"📖 <b>{category_name}:</b>\n\nQuiz tanlang:",
            reply_markup=keyboard,
        )
        
        # Store quizzes in state
        await state.update_data(quizzes=quizzes, category=category)
        await state.set_state(QuizState.selecting_quiz)
        
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ Xato yuz berdi.")


@dp.message(QuizState.selecting_quiz)
async def quiz_selection_handler(message: Message, state: FSMContext):
    """Handle quiz selection"""
    if (message.text or "").strip() == "⬅️ Orqaga":
        await message.answer(
            "Kategoriya tanlang:",
            reply_markup=await get_categories_keyboard(),
        )
        await state.set_state(QuizState.selecting_category)
        return
    
    quiz_name = (message.text or "").strip().replace("📝 ", "")
    data = await state.get_data()
    quizzes = data.get("quizzes", [])
    
    quiz = next((q for q in quizzes if q["title"] == quiz_name), None)
    if not quiz:
        await message.answer("❌ Quiz topilmadi.")
        return
    
    session = get_user_session(message.from_user.id)
    session.quiz_id = quiz["id"]
    
    try:
        # Start attempt
        response = requests.post(
            f"{API_BASE}/v2/attempts/start",
            json={"quiz_id": quiz["id"], "student_email": session.student_email},
            timeout=10
        )
        
        if response.status_code != 200:
            await message.answer("❌ Quiz boshlashda xato.")
            return
        
        attempt_data = response.json()
        session.attempt_id = attempt_data["attempt_id"]
        session.started_at = datetime.now()
        
        # Get questions
        response = requests.get(
            f"{API_BASE}/v2/attempts/{session.attempt_id}/questions",
            timeout=10
        )
        
        if response.status_code != 200:
            await message.answer("❌ Savollarni yuklab olishda xato.")
            return
        
        session.questions = response.json()
        session.current_question_index = 0
        
        if not session.questions:
            await message.answer("❌ Quiz da savol yo'q.")
            return
        
        # Show first question
        await show_question(message, state)
        
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ Xato yuz berdi.")


async def show_question(message: types.Message, state: FSMContext):
    """Show current question"""
    user_id = message.from_user.id
    session = get_user_session(user_id)
    
    if session.current_question_index >= len(session.questions):
        await finish_quiz(message, state)
        return
    
    question = session.questions[session.current_question_index]
    
    # Create inline keyboard with answers
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{chr(65 + i)}. {answer['text']}",
            callback_data=f"answer_{answer['id']}"
        )]
        for i, answer in enumerate(question['answers'])
    ])
    
    progress = f"{session.current_question_index + 1}/{len(session.questions)}"
    
    text = (
        f"❓ <b>Savol #{session.current_question_index + 1}</b> [{progress}]\n\n"
        f"<b>{question['text']}</b>\n\n"
        f"<i>Javob tanlang:</i>"
    )
    
    if question.get('image_url'):
        await message.answer_photo(
            photo=question['image_url'],
            caption=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(text, reply_markup=keyboard)


@dp.callback_query(QuizState.answering_question)
async def answer_handler(callback: CallbackQuery, state: FSMContext):
    """Handle answer submission"""
    user_id = callback.from_user.id
    session = get_user_session(user_id)
    
    # Extract answer ID
    answer_id = int(callback.data.split("_")[1])
    question = session.questions[session.current_question_index]
    
    try:
        # Submit answer
        response = requests.post(
            f"{API_BASE}/v2/attempts/{session.attempt_id}/answer",
            json={
                "question_id": question["id"],
                "selected_answer_id": answer_id
            },
            timeout=10
        )
        
        if response.status_code != 200:
            await callback.answer("❌ Javob qabul qilinmadi.", show_alert=True)
            return
        
        result = response.json()
        
        # Show result
        status = "✅ To'g'ri!" if result["is_correct"] else "❌ Noto'g'ri!"
        
        await callback.message.edit_text(
            f"{status}\n\n"
            f"Hozirgi ball: <b>{result['score']}</b>\n"
            f"To'g'ri: {result['correct_count']} | Noto'g'ri: {result['wrong_count']}",
            parse_mode=ParseMode.HTML,
        )
        
        session.current_question_index += 1
        
        # Wait 1 second then show next question
        await asyncio.sleep(1)
        
        if session.current_question_index < len(session.questions):
            # Show next question
            await show_question(callback.message, state)
            await state.set_state(QuizState.answering_question)
        else:
            # Finish quiz
            await finish_quiz(callback.message, state)
        
        await callback.answer()
        
    except Exception as e:
        print(f"Error: {e}")
        await callback.answer("❌ Xato yuz berdi.", show_alert=True)


@dp.message(QuizState.answering_question)
async def skip_question_handler(message: Message, state: FSMContext):
    """Handle message during quiz"""
    if (message.text or "").strip() == "⬅️ Orqaga":
        user_id = message.from_user.id
        session = get_user_session(user_id)
        
        # Finish quiz
        await finish_quiz(message, state)
        return
    
    await message.answer("❌ Javobni tugmani bosib tanlang.")


async def finish_quiz(message: types.Message, state: FSMContext):
    """Finish quiz and show results"""
    user_id = message.from_user.id
    session = get_user_session(user_id)
    
    try:
        # Finish attempt
        response = requests.post(
            f"{API_BASE}/v2/attempts/{session.attempt_id}/finish",
            timeout=10
        )
        
        if response.status_code != 200:
            await message.answer("❌ Quiz yakunlashda xato.")
            return
        
        result = response.json()
        
        text = (
            f"🎉 <b>Quiz yakunlandi!</b>\n\n"
            f"📊 <b>Natijar:</b>\n"
            f"Ball: <b>{result['score']}</b>\n"
            f"Foiz: <b>{result['percentage']}%</b>\n"
            f"To'g'ri: {result['correct_count']}\n"
            f"Noto'g'ri: {result['wrong_count']}\n"
            f"Vaqt: {result['duration']} soniya\n\n"
            f"✨ Mukammal! Endi boshqa kategoriyani tanlang."
        )
        
        await message.answer(text, reply_markup=await get_categories_keyboard())
        await state.set_state(QuizState.selecting_category)
        
    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ Xato yuz berdi.")
        await state.clear()


@dp.message(Command("profile"))
async def profile_handler(message: Message):
    """Show user profile"""
    # TODO: Implement profile endpoint
    await message.answer("👤 Profil shakl etilmoqda...")


@dp.message(Command("help"))
async def help_handler(message: Message):
    """Show help"""
    await message.answer(
        "ℹ️ <b>YORDAM</b>\n\n"
        "/start - Boshidan boshlash\n"
        "/profile - Mening profilim\n"
        "/leaderboard - Reyting\n"
        "/help - Yordam\n\n"
        "Quizlar orqali bilim sinab ko'ring va reyting topida chiqing! 🚀"
    )


@dp.message()
async def message_handler(message: Message, state: FSMContext):
    """Handle any other messages"""
    current_state = await state.get_state()
    
    if not current_state:
        await message.answer("Menyu:", reply_markup=main_keyboard())


async def main():
    """Start bot"""
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 Boshida boshlash"),
        BotCommand(command="profile", description="👤 Mening profilim"),
        BotCommand(command="help", description="❓ Yordam"),
    ])
    
    print("🤖 Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
