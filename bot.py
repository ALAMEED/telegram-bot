import telebot
import google.generativeai as genai
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TELEGRAM_TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'
GEMINI_API_KEY = 'AIzaSyCvCjxg2YvkrkyDnBcDBntS0x4JGUHsRdU'

# إعداد محرك جوجل Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# سيرفر النبض لـ Render لضمان التشغيل 24 ساعة
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Hassoun Gemini is Live")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthCheckHandler).serve_forever()

# --- دالة الذكاء الاصطناعي (Gemini) ---
def get_gemini_response(user_text):
    try:
        # نظام التوجيه للهجة العراقية
        prompt = f"أنت حسون AI، مساعد ذكي ومرح، تتحدث باللهجة العراقية الشعبية فقط. أجب على هذا السؤال: {user_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return "🤖 يا غالي، صار عندي فصل بالوايرات وية سيرفرات جوجل. ارجع دز رسالتك ثواني."

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا والله بالهندسة! 💡🛠️\nأنا حسون AI بنسختي الجديدة المستقرة (Gemini).\nاسألني أي شي وهسة أجاوبك وبسرعة البرق!")

@bot.message_handler(func=lambda m: True)
def chat(message):
    if "http" in message.text:
        bot.reply_to(message, "⚠️ حبيبي، هذا البوت للدردشة بس. بوت التحميل راح نكمله بالخطوة الجاية.")
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    # جلب الرد من جوجل
    answer = get_gemini_response(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    # تشغيل سيرفر النبض
    threading.Thread(target=run_health_server, daemon=True).start()
    print("تم الربط بمحركات جوجل بنجاح! 🚀")
    # تشغيل البوت
    bot.infinity_polling()
