import telebot
from telebot import types
import requests

# --- الإعدادات ---
# قمت بإضافة .strip() لحذف أي مسافات زائدة قد تسبب الخطأ الذي ظهر عندك
TOKEN = '1095568264:AAGF8NrtR2537DD1PzuzywRgbGMY_0IdivE'.strip()
ADMIN_ID = 818416878 
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# فحص الاشتراك
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا ✅", url=f"https://t.me/{CHANNEL_ID}"))
        return bot.send_message(message.chat.id, "⚠️ يرجى الاشتراك أولاً لتفعيل البوت.", reply_markup=markup)
    bot.reply_to(message, "أهلاً حسين! أنا الآن بوت ذكاء اصطناعي نصي شامل (مثل ChatGPT). اسألني عن أي شيء!")

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    bot.send_chat_action(message.chat.id, 'typing')
    
    # نستخدم requests للاتصال المباشر لنتجنب خطأ "ModuleNotFoundError: openai"
    try:
        url = f"https://text.pollinations.ai/{message.text}?model=openai&search=true"
        response = requests.get(url, timeout=30)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "🤖 السيرفر مشغول حالياً، حاول مجدداً لاحقاً.")

if __name__ == "__main__":
    bot.infinity_polling()
