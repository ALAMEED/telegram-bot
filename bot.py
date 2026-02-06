import telebot
from telebot import types
import requests
import yt_dlp
import os

# --- الإعدادات ---
TOKEN = '1095568264:AAFfnXrbl_VJ4L8qzjvcDZ_mpe_IPRttEgc'.strip()
ADMIN_ID = 818416878 
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# فحص الاشتراك الإجباري
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا لتفعيل البوت ✅", url=f"https://t.me/{CHANNEL_ID}"))
        return bot.send_message(message.chat.id, "⚠️ أهلاً بك! يرجى الاشتراك أولاً لاستخدام مميزات التحميل والذكاء الاصطناعي.", reply_markup=markup)
    
    bot.reply_to(message, "أهلاً بك يا حسين في البوت الشامل! 🚀\n\n1️⃣ **للدردشة:** أرسل أي سؤال بأي لغة أو لهجة.\n2️⃣ **للتحميل:** أرسل رابط الفيديو (تيك توك، إنستا، يوتيوب) وسأقوم بجلب الملف لك.")

# --- قسم تحميل الفيديوهات ---
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'max_filesize': 45 * 1024 * 1024  # حد أقصى 45 ميجا لكي لا ينهار سيرفر ريندر
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    if not is_subscribed(message.from_user.id): return
    
    url = message.text
    msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتحميل الفيديو... انتظر قليلاً.")
    
    try:
        video_file = download_video(url)
        with open(video_file, 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ تم التحميل بواسطة حسون AI")
        os.remove(video_file) # حذف الملف بعد الإرسال لتوفير المساحة
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ عذراً، لم أستطع تحميل هذا الفيديو. تأكد من أن الرابط مباشر أو أن الفيديو ليس طويلاً جداً.", message.chat.id, msg.message_id)

# --- قسم الذكاء الاصطناعي الشامل (كافة اللغات واللهجات) ---
@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # محرك ذكاء اصطناعي متطور جداً يدعم اللهجات (العراقية، الخليجية، المصرية.. إلخ)
    user_query = message.text
    system_prompt = "أنت مساعد ذكي اسمك حسون AI. تتحدث بطلاقة مع المستخدمين بكافة اللغات واللهجات وخصوصاً اللهجة العراقية. كن ودوداً وذكياً جداً."
    api_url = f"https://text.pollinations.ai/{user_query}?model=openai&system={system_prompt}"
    
    try:
        response = requests.get(api_url, timeout=25)
        if response.status_code == 200:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "🤖 السيرفر مزدحم، جرب تسألني مرة ثانية.")
    except:
        bot.reply_to(message, "⚠️ فشل في الاتصال بالذكاء الاصطناعي.")

if __name__ == "__main__":
    bot.infinity_polling()
