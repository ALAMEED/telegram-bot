import telebot
import google.generativeai as genai
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. الإعدادات (تأكد من صحتها) ---
TELEGRAM_TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'
GEMINI_API_KEY = 'AIzaSyCvCjxg2YvkrkyDnBcDBntS0x4JGUHsRdU'

# إعداد محرك جوجل Gemini
genai.configure(api_key=GEMINI_API_KEY)
# استخدمنا موديل flash لأنه الأسرع والأقل استهلاكاً للموارد
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- 2. سيرفر النبض لـ Render (للحفاظ على استمرارية الخدمة) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hassoun Gemini AI is Live and Ready")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    httpd.serve_forever()

# --- 3. دالة الذكاء الاصطناعي (مع صمام أمان للردود الفارغة) ---
def get_ai_response(user_text):
    try:
        # توجيه المحرك للهجة العراقية
        prompt = f"أنت حسون AI، مساعد ذكي ومرح، تتحدث باللهجة العراقية الشعبية فقط. أجب باختصار على هذا السؤال: {user_text}"
        
        response = model.generate_content(prompt)
        
        # فحص إذا كان هناك رد فعلي من المحرك
        if response and response.text and len(response.text.strip()) > 0:
            return response.text.strip()
        else:
            return "🤖 اعتذر منك يا غالي، جوجل ما انطاني رد هالمرة. جرب تعيد السؤال بغير صيغة."
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        # إذا فشل جوجل، هذا رد احتياطي بسيط
        return "⚠️ يبدو أن الربط مع السيرفر العالمي فيه خلل بسيط. ارجع دز رسالتك بعد ثواني."

# --- 4. معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_msg = (
        "هلا والله بالهندسة! نورت حسون AI 💡🛠️\n\n"
        "تم الربط بنجاح بمحركات جوجل العالمية 🌍\n"
        "اسألني أي شي وبالعراقي وأبشر بالرد السريع."
    )
    bot.reply_to(message, welcome_msg)

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    # التأكد من وجود نص في الرسالة المستلمة
    if not message.text:
        return

    # استبعاد الروابط مؤقتاً (لأن هذا بوت دردشة)
    if "http" in message.text.lower():
        bot.reply_to(message, "⚠️ حبيبي، أنا مخصص للدردشة بس. بوت التحميل راح نكمله بالخطوة الجاية.")
        return

    # إظهار حالة "يكتب الآن" (Typing)
    try:
        bot.send_chat_action(message.chat.id, 'typing')
    except:
        pass
    
    # جلب الرد من الذكاء الاصطناعي
    answer = get_ai_response(message.text)
    
    # فحص نهائي: إذا كان الرد فارغاً (لتجنب خطأ 400 Bad Request)
    if not answer or not answer.strip():
        answer = "🤖 الرد طلع فارغ من السيرفر، جرب تسألني (هلو) حتى نختبر الاتصال."

    try:
        bot.reply_to(message, answer)
    except Exception as e:
        print(f"Telegram Send Error: {e}")

# --- 5. تشغيل النظام ---
if __name__ == "__main__":
    # تشغيل سيرفر النبض في خلفية الكود
    threading.Thread(target=run_health_server, daemon=True).start()
    print("الترسانة انطلقت بنجاح! 🚀")
    
    # تشغيل البوت مع خاصية التكرار التلقائي في حال الفصل
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
