import telebot
from telebot import types
import requests
import yt_dlp
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات بالتوكن الجديد (حسين: تأكد أن التوكن صحيح) ---
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'.strip()
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# --- نظام الحفاظ على البوت نشطاً في Render (فتح بورت وهمي) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hassoun AI System is Online")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- فحص الاشتراك الإجباري ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except: 
        return True # إذا فشل الفحص، يشتغل البوت تلقائياً

# --- نظام الذكاء الاصطناعي (ترسانة المحركات) ---
def get_ai_response(query):
    # مصفوفة المحركات بالترتيب (الأفضل فالأسرع)
    system_prompt = "أنت حسون AI، مساعد ذكي ومرح تتحدث باللهجة العراقية بطلاقة."
    engines = [
        {"name": "DeepSeek", "url": f"https://text.pollinations.ai/{query}?model=deepseek&system={system_prompt}"},
        {"name": "Gemini", "url": f"https://text.pollinations.ai/{query}?model=gemini&system={system_prompt}"},
        {"name": "OpenAI", "url": f"https://text.pollinations.ai/{query}?model=openai&system={system_prompt}"},
        {"name": "SearchGPT", "url": f"https://text.pollinations.ai/{query}?model=searchgpt&system={system_prompt}"}
    ]
    
    for engine in engines:
        try:
            # زدنا وقت الانتظار لـ 25 ثانية لضمان استلام الرد
            response = requests.get(engine["url"], timeout=25)
            if response.status_code == 200 and len(response.text.strip()) > 2:
                return response.text
        except:
            print(f"فشل محرك {engine['name']}.. جاري تجربة المحرك التالي")
            continue
            
    return "🤖 يا غالي، ارجع دز سؤالك هسة، السيرفرات جانت عليها ضغط وفتحت!"

# --- الأوامر الرئيسية ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا ✅", url=f"https://t.me/{CHANNEL_ID}"))
        return bot.send_message(message.chat.id, f"⚠️ أهلاً {user_name}! يرجى الاشتراك في القناة أولاً لتفعيل مميزات البوت.", reply_markup=markup)
    
    bot.reply_to(message, f"هلا والله {user_name}! نورت بوت حسون AI المطور 🚀\n\n- اسألني أي شي وبالعراقي.\n- دزلي رابط فيديو حتى أحمله إلك.")

# --- نظام تحميل الفيديوهات ---
@bot.message_handler(func=lambda m: "http" in m.text)
def handle_download(message):
    if not is_subscribed(message.from_user.id): return
    
    msg = bot.reply_to(message, "⏳ جارِ التحميل من السيرفر.. تدلل.")
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'vid_file.mp4',
            'max_filesize': 48 * 1024 * 1024, # 48 ميجا كحد أقصى
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        
        with open('vid_file.mp4', 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ تم التحميل بواسطة حسون AI")
        
        os.remove('vid_file.mp4')
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ عذراً! الرابط غير مدعوم أو حجم الفيديو كبير جداً.", message.chat.id, msg.message_id)

# --- نظام الدردشة الذكي ---
@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # الحصول على أفضل استجابة من الترسانة
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

# --- تشغيل البوت مع السيرفر الوهمي ---
if __name__ == "__main__":
    # تشغيل سيرفر النبض في الخلفية لإرضاء Render
    threading.Thread(target=run_health_server, daemon=True).start()
    print("نظام حسون AI الخماسي انطلق بالتوكن الجديد! 🚀")
    bot.infinity_polling()
