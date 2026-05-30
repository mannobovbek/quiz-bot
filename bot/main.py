from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import BOT_TOKEN, CHANNEL_ID
import asyncio

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

async def check_sub(user_id):
    member = await bot.get_chat_member(CHANNEL_ID, user_id)
    return member.status in ["member", "administrator", "creator"]

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "🏛 <b>Registon Imtihon Markazi</b>\n\n📚 Online Quiz Platform"
    )

@dp.message()
async def quiz_handler(message: Message):
    if message.text == "quiz":
        await bot.send_poll(
            chat_id=message.chat.id,
            question="Python qachon yaratilgan?",
            options=["1991", "2001", "2010", "1985"],
            type="quiz",
            correct_option_id=0,
            explanation="To'g'ri javob: 1991"
        )

async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Start"),
        BotCommand(command="admin", description="Admin Panel")
    ])

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())