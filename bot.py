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
        self.send_response(200); self.end_headers(); self.wfile.write(b"AI Chat Bot is Live")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthCheckHandler).serve_forever()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا بيك! أنا حسون AI، مخصص فقط للدردشة والذكاء الاصطناعي. اسألني أي شي.")

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    bot.send_chat_action(message.chat.id, 'typing')
    query = message.text
    # محرك GPT-4o خفيف وسريع
    url = f"https://text.pollinations.ai/{query}?model=openai&system=أنت حسون AI، تتحدث بلهجة عراقية محبوبة وقصيرة."
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "🤖 حبيبي، السيرفر شوية تعبان، ارجع دز رسالتك.")
    except:
        bot.reply_to(message, "⚠️ صار فصل بالشبكة، دزها مرة ثانية.")

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    bot.infinity_polling()
