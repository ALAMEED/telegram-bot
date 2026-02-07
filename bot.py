import telebot
import requests
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- الإعدادات ---
TOKEN = '8490406462:AAFgxnr3RZpcwVdHDERah6xhCC7QXkmdb0A'
bot = telebot.TeleBot(TOKEN)

# سيرفر النبض لـ Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"World Engines AI is Online")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthCheckHandler).serve_forever()

# --- مصفوفة المحركات العالمية ---
def get_world_ai_response(query):
    # قائمة بأسماء الموديلات المتاحة عالمياً عبر التوصيل المجاني
    models = ["deepseek", "openai", "claude", "gemini", "llama"]
    system_prompt = "أنت حسون AI المطور، مساعد ذكي جداً تتحدث باللهجة العراقية ببراعة وتساعد المستخدمين بكل إخلاص."

    for model_name in models:
        try:
            # نرسل الطلب للمحرك الحالي
            url = f"https://text.pollinations.ai/{query}?model={model_name}&system={system_prompt}"
            response = requests.get(url, timeout=12) # وقت استجابة سريع للتبديل
            
            if response.status_code == 200 and len(response.text.strip()) > 5:
                print(f"✅ تمت الاستجابة بواسطة محرك: {model_name}")
                return response.text
        except:
            print(f"❌ فشل محرك {model_name}.. جاري التحويل للمحرك التالي.")
            continue
            
    return "🤖 يا غالي، يبدو أن جميع المحركات العالمية (DeepSeek, GPT, Gemini) مشغولة حالياً. ارجع دز سؤالك بعد لحظات."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك في النسخة العالمية من حسون AI 🌍🚀\n\nتم ربط البوت بـ (DeepSeek, GPT-4, Gemini, Claude, Llama).\n\nاسألني أي سؤال وراح أجاوبك بأفضل محرك متاح!")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    if "http" in message.text:
        return bot.reply_to(message, "⚠️ حبيبي هذا بوت دردشة بس. بوت التحميل راح نخلصه ورا هذا مباشرة.")
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # استدعاء الترسانة
    answer = get_world_ai_response(message.text)
    bot.reply_to(message, answer)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    print("الترسانة العالمية جاهزة للانطلاق! 🚀")
    bot.infinity_polling()
