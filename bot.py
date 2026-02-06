import telebot
from telebot import types
import requests
import yt_dlp
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'.strip()
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# --- نظام الحماية من توقف Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Super AI Bot is Online")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthCheckHandler).serve_forever()

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True

# --- مصفوفة المحركات "الترسانة الشاملة" ---
def get_ai_response(query):
    # ترتيب المحركات من الأذكى للأسرع
    engines = [
        {"name": "DeepSeek", "model": "deepseek"},
        {"name": "Gemini", "model": "gemini"},
        {"name": "ChatGPT-4o", "model": "openai"},
        {"name": "Llama-3.3", "model": "llama"},
        {"name": "SearchGPT", "model": "searchgpt"}
    ]
    
    system_msg = "أنت حسون AI، مساعد ذكي جداً تتحدث باللهجة العراقية بطلاقة وتساعد المستخدمين بكل حب."
    
    for engine in engines:
        try:
            # محاولة جلب الإجابة من المحرك الحالي
            api_url = f"https://text.pollinations.ai/{query}?model={engine['model']}&system={system_msg}"
            response = requests.get(api_url, timeout=12) # وقت انتظار قصير لضمان سرعة التبديل
            
            if response.status_code == 200 and len(response.text) > 2:
                # نرسل الإجابة مع توضيح المحرك (اختياري، يمكنك حذفه)
                return response.text
        except:
            print(f"فشل {engine['name']}.. جاري الانتقال للبديل")
            continue 
            
    return "🤖 يا غالي، يبدو أن هناك ضغطاً عالمياً على جميع المحركات. أعد إرسال سؤالك الآن وسأحاول مجدداً!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا بيك بالنسخة الأسطورية! 🚀\nأنا حسون AI، تم دمج محركات:\n(DeepSeek, Gemini, ChatGPT, Llama)\n\nدزلي أي سؤال أو رابط فيديو لتحميله.")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_download(message):
    if not is_subscribed(message.from_user.id): return
    msg = bot.reply_to(message, "⏳ جاري التحميل من أقوى السيرفرات...")
    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 48*1024*1024, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([message.text])
        with open('video.mp4', 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ تم التحميل بنجاح بواسطة حسون AI")
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ عذراً، هذا الرابط غير مدعوم أو الفيديو ثقيل جداً.", message.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    bot.send_chat_action(message.chat.id, 'typing')
    
    # الحصول على إجابة من نظام المحركات المتعددة
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    print("نظام المحركات الخماسي انطلق! 🚀")
    bot.infinity_polling()
