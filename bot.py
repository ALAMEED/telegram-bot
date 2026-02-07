import telebot
import requests
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
# تأكد من وضع التوكن الصحيح هنا
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'
bot = telebot.TeleBot(TOKEN)

# --- سيرفر النبض لـ Render (للحفاظ على استمرارية الخدمة) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hassoun Engine is Running")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- محرك الذكاء الاصطناعي (الربط المباشر) ---
def get_ai_response(user_query):
    # نظام الـ Seed العشوائي لكسر حظر السيرفرات وتجديد الاستجابة
    random_seed = int(time.time())
    system_prompt = "أنت حسون AI، مساعد تقني ذكي تتحدث اللهجة العراقية ببراعة. جاوب باختصار ومودة."
    
    # المحرك الأساسي: OpenAI (عبر مسار سريع)
    primary_url = f"https://text.pollinations.ai/{user_query}?model=openai&system={system_prompt}&seed={random_seed}"
    
    # المحرك البديل: Mistral (سريع جداً وخفيف)
    backup_url = f"https://text.pollinations.ai/{user_query}?model=mistral&system={system_prompt}"

    try:
        # المحاولة الأولى
        response = requests.get(primary_url, timeout=15)
        if response.status_code == 200 and len(response.text.strip()) > 1:
            return response.text
    except:
        pass

    try:
        # المحاولة الثانية (ربط توازي في حال فشل الأول)
        response = requests.get(backup_url, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        return "🤖 يا غالي، السيرفر بي شوية ضغط. ارجع دز رسالتك هسة ومية بالمية أجاوبك!"

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "هلا والله بالهندسة! 💡🛠️\nأنا حسون AI، جاهز لأي سؤال ببالك. اسألني أي شي هسة.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    # تجاهل الروابط في بوت الدردشة
    if "http" in message.text:
        bot.reply_to(message, "⚠️ حبيبي، هذا البوت للدردشة بس. بوت التحميل راح نكمله بالخطوة الجاية.")
        return

    # إظهار حالة "يكتب الآن"
    bot.send_chat_action(message.chat.id, 'typing')
    
    # جلب الرد
    answer = get_ai_response(message.text)
    bot.reply_to(message, answer)

# --- تشغيل النظام ---
if __name__ == "__main__":
    # تشغيل سيرفر الصحة في خلفية الكود
    threading.Thread(target=run_health_server, daemon=True).start()
    print("تم تشغيل الترسانة بنجاح! 🚀")
    
    # تشغيل البوت مع خاصية عدم التوقف
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
