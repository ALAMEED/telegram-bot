import telebot
import requests
import os
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. الإعدادات ---
# التوكن مالتك شغال 100%
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'
bot = telebot.TeleBot(TOKEN)

# --- 2. سيرفر النبض لـ Render ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hassoun AI is Online")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- 3. محرك الذكاء الاصطناعي (نظام الربط المستقر) ---
def get_world_ai_response(query):
    try:
        # تشفير النص (Encoding) لمنع الأخطاء في الحروف العربية والمسافات
        safe_query = urllib.parse.quote(query)
        
        # نظام التوجيه (System Prompt) ليكون الرد عراقي
        system_prompt = urllib.parse.quote("أنت حسون AI، مساعد ذكي تتحدث اللهجة العراقية بأسلوب تقني ومرح.")
        
        # استخدام محرك Pollinations المباشر (أكثر استقراراً من DeepSeek حالياً)
        url = f"https://text.pollinations.ai/{safe_query}?model=openai&system={system_prompt}&seed=123"
        
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
        else:
            # محاولة بمحرك بديل في حال فشل الأول (Llama 3)
            backup_url = f"https://text.pollinations.ai/{safe_query}?model=llama"
            backup_res = requests.get(backup_url, timeout=15)
            return backup_res.text.strip() if backup_res.status_code == 200 else "🤖 يا غالي، السيرفر العالمي بيه ضغط، ثواني وارجع دز رسالتك."

    except Exception as e:
        print(f"Error: {e}")
        return "🤖 حبيبي، اكو خلل بالربط، لحظات وجرب مرة ثانية."

# --- 4. معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "هلا والله بالهندسة! نورت حسون AI 💡\nأنا جاهز ومستقر هسة، اسألني أي شي وبالعراقي.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    # إظهار حالة "يكتب الآن"
    try:
        bot.send_chat_action(message.chat.id, 'typing')
    except:
        pass

    # جلب الرد
    answer = get_world_ai_response(message.text)
    
    # فحص نهائي للتأكد أن الرسالة ليست فارغة
    if answer and len(answer.strip()) > 0:
        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "🤖 السيرفر جاوبني برد فارغ، جرب تغير صيغة السؤال.")

# --- 5. التشغيل ---
if __name__ == "__main__":
    # تشغيل سيرفر الصحة بالخلفية
    threading.Thread(target=run_health_server, daemon=True).start()
    print("البوت انطلق بنجاح! 🚀")
    
    # تنظيف أي Webhook قديم لتجنب خطأ 409
    bot.remove_webhook()
    # تشغيل البوت
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
