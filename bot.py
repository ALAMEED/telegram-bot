import telebot
from telebot import types
import requests
import yt_dlp
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TOKEN = '1095568264:AAFfnXrbl_VJ4L8qzjvcDZ_mpe_IPRttEgc'.strip()
ADMIN_ID = 818416878 
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# --- نظام خداع Render (فتح بورت وهمي) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hassoun AI is Alive!")

def run_health_server():
    # Render يعطي البورت في المتغير البيئي PORT، وإذا لم يجده يستخدم 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- فحص الاشتراك ---
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
        return bot.send_message(message.chat.id, "⚠️ اشترك بالقناة أولاً لتفعيل البوت!", reply_markup=markup)
    bot.reply_to(message, "هلا بيك! أنا حسون AI الشامل. أرسل سؤالك أو رابط فيديو لتحميله! 🚀")

# --- نظام التحميل ---
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.mp4',
        'quiet': True,
        'max_filesize': 48 * 1024 * 1024 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    if not is_subscribed(message.from_user.id): return
    msg = bot.reply_to(message, "⏳ جارِ التحميل... تدلل.")
    try:
        video_file = download_video(message.text)
        with open(video_file, 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ تم التحميل بواسطة حسون AI")
        os.remove(video_file)
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ عذراً، حجم الفيديو كبير أو الرابط غير مدعوم.", message.chat.id, msg.message_id)

# --- نظام الدردشة ---
@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    bot.send_chat_action(message.chat.id, 'typing')
    
    api_url = f"https://text.pollinations.ai/{message.text}?model=llama&system=Talk%20in%20Iraqi%20dialect%20as%20Hassoun%20AI"
    
    try:
        response = requests.get(api_url, timeout=15)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "🤖 السيرفر مشغول، أعد إرسال سؤالك هسة.")

# --- تشغيل البوت مع السيرفر الوهمي ---
if __name__ == "__main__":
    # تشغيل سيرفر البورت في خلفية الكود
    threading.Thread(target=run_health_server, daemon=True).start()
    print("السيرفر الوهمي اشتغل... البوت ينطلق الآن!")
    bot.infinity_polling()
