import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize bot & dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# SQLite database
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)"
)
conn.commit()


def get_balance(user_id: int) -> int:
    c.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0


def add_balance(user_id: int, amount: int):
    c.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?,0)", (user_id,))
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    conn.commit()


@router.message(Command("start"))
async def start_handler(msg: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🎬 Watch Ads",
        web_app=WebAppInfo(url="https://68d6bad04164d67d4ae0f7cd--merry-dasik-4cd1d1.netlify.app/"),
    )
    await msg.answer("👋 Welcome! Earn by watching ads.", reply_markup=kb.as_markup())


@router.message(Command("balance"))
async def balance_handler(msg: types.Message):
    bal = get_balance(msg.from_user.id)
    await msg.answer(f"💰 Your balance: {bal} coins")


@router.message(lambda m: m.web_app_data is not None)
async def webapp_data_handler(msg: types.Message):
    if msg.web_app_data.data == "ad_watched":
        add_balance(msg.from_user.id, 1)
        await msg.answer("✅ Thanks! Balance updated.")


async def main():
    await dp.start_polling(bot)


if name == "main":
    asyncio.run(main())
