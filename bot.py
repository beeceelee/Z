from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.utils import executor
import sqlite3
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# SQLite database
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
conn.commit()

def get_balance(user_id):
    c.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

def add_balance(user_id, amount):
    c.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?,0)", (user_id,))
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
    conn.commit()

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="🎬 Watch Ads",
        web_app=WebAppInfo(url="https://68d6bad04164d67d4ae0f7cd--merry-dasik-4cd1d1.netlify.app/")  # replace with hosted WebApp
    ))
    await msg.answer("👋 Welcome! Earn by watching ads.", reply_markup=kb)

@dp.message_handler(commands=["balance"])
async def balance(msg: types.Message):
    bal = get_balance(msg.from_user.id)
    await msg.answer(f"💰 Your balance: {bal} coins")

@dp.message_handler(content_types="web_app_data")
async def webapp_data(msg: types.Message):
    if msg.web_app_data.data == "ad_watched":
        add_balance(msg.from_user.id, 1)
        await msg.answer("✅ Thanks! Balance updated.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
