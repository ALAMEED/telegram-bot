import telebot
from telebot import types
import requests
import sqlite3
import os
from urllib.parse import quote
import openai
from datetime import datetime

# ====== إعدادات ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

ADMIN_ID = 818416878
CHANNEL_ID = "ALAMEED_FM"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
openai.api_key = OPENAI_KEY

# ====== قاعدة البيانات ======
db = sqlite3.connect("bot.db", check_same_thread=False)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    joined_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    time TEXT
)
""")

db.commit()

# ====== فحص الاشتراك ======
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# ====== حفظ الرسائل ======
def save_message(user_id, role, content):
    cursor.execute(
        "INSERT INTO messages (user_id, role, content, time) VALUES (?, ?, ?, ?)",
        (user_id, role, content, datetime.now().isoformat())
    )
    db.commit()

def get_context(user_id, limit=10):
    cursor.execute(
        "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()[::-1]
    return [{"role": r, "content": c} for r, c in rows]

def ask_ai(user_id, prompt):
    context = get_context(user_id)

    messages = [
        {"role": "system", "content": "أنت مساعد عربي ذكي، دقيق، مختصر، ومفيد."}
    ] + context + [
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content

# ====== أوامر البوت ======
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user.id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user.id, user.first_name, datetime.now().isoformat())
        )
        db.commit()

        if user.id != ADMIN_ID:
            bot.send_message(
                ADMIN_ID,
                f"👤 مستخدم جديد\n{user.first_name}\n`{user.id}`"
            )

    if not is_subscribed(user.id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(
            "اشترك بالقناة ✅",
            url=f"https://t.me/{CHANNEL_ID}"
        ))
        bot.send_message(
            message.chat.id,
            "⚠️ اشترك بالقناة أولاً.",
            reply_markup=kb
        )
        return

    bot.reply_to(message, "🤖 أهلاً! اكتب سؤالك وسأتذكر حديثك 😉")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    bot.reply_to(message, f"📊 عدد المستخدمين: {users}")

@bot.message_handler(commands=['clear'])
def clear(message):
    cursor.execute("DELETE FROM messages WHERE user_id=?", (message.from_user.id,))
    db.commit()
    bot.reply_to(message, "🧹 تم مسح الذاكرة.")

@bot.message_handler(func=lambda m: True)
def chat(message):
    if not message.text:
        bot.reply_to(message, "📌 أرسل نص فقط.")
        return

    if not is_subscribed(message.from_user.id):
        return

    bot.send_chat_action(message.chat.id, 'typing')
    save_message(message.from_user.id, "user", message.text)

    try:
        answer = ask_ai(message.from_user.id, message.text)
    except:
        q = quote(message.text)
        r = requests.get(f"https://text.pollinations.ai/{q}")
        answer = r.text if r.status_code == 200 else "❌ فشل الاتصال."

    save_message(message.from_user.id, "assistant", answer)

    for i in range(0, len(answer), 4000):
        bot.send_message(message.chat.id, answer[i:i+4000])

print("🤖 البوت شغال...")
bot.infinity_polling()
