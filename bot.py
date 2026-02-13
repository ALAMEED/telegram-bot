import telebot
import requests
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A' # تأكد إن هذا التوكن الجديد
bot = telebot.TeleBot(TOKEN)

# سيرفر النبض لـ Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Hassoun is Live")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthCheckHandler).serve_forever()

# --- دالة الرد الذكي (نسخة مستقرة جداً) ---
def get_ai_answer(user_message):
    try:
        # الربط مع محرك ذكاء اصطناعي مفتوح ومستقر
        url = "https://api.blackbox.ai/api/chat"
        payload = {
            "messages": [
                {"role": "system", "content": "أنت حسون AI، مساعد تقني عراقي ذكي ومرح. تجيب باللهجة العراقية فقط."},
                {"role": "user", "content": user_message}
            ],
            "model": "deepseek-v3", # أو "gpt-4o"
            "max_tokens": 500
        }
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=15)
        
        if response.status_code == 200:
            # تنظيف الرد من أي أكواد برمجية زايدة
            full_response = response.text.strip()
            # في بعض الأحيان الرد يكون JSON، نحتاج نطلعه صافي
            try:
                data = json.loads(full_response)
                return data.get('content', full_response)
            except:
                return full_response
        else:
            return "🤖 السيرفر العالمي شوية ثقيل، ارجع دز رسالتك عيوني."
            
    except Exception as e:
        print(f"Error AI: {e}")
        return "⚠️ اكو مشكلة بربط الدائرة البرمجية، ثواني وارجع."

# --- معالجة الرسائل ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "هلا بيك يا هندسة! 🛠️\nحسون AI جاهز للدردشة. اسأل أي شي.")

@bot.message_handler(func=lambda m: True)
def chat_handler(message):
    if not message.text: return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # جلب الجواب من المحرك
    answer = get_ai_answer(message.text)
    
    # فحص إذا الرد فارغ (تجنب خطأ 400)
    if answer and answer.strip():
        bot.reply_to(message, answer)
    else:
        bot.reply_to(message, "🤖 اعتذر، الرد ضاع بالطريق. جرب مرة ثانية.")

if __name__ == "__main__":
    # تشغيل النبض
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # أهم خطوة لإنهاء الـ 409
    bot.remove_webhook()
    print("البوت انطلق..")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
