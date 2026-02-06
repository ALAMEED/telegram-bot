import telebot
from telebot import types
import requests
import yt_dlp
import os
import time

# --- الإعدادات النهائية ---
# التوكن الجديد مدمج وجاهز
TOKEN = '1095568264:AAFfnXrbl_VJ4L8qzjvcDZ_mpe_IPRttEgc'.strip()
ADMIN_ID = 818416878 
CHANNEL_ID = 'ALAMEED_FM'

bot = telebot.TeleBot(TOKEN)

# فحص الاشتراك الإجباري
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_ID}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except: 
        return True # في حال وجود خطأ في الفحص يعمل البوت تلقائياً

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك هنا لتفعيل البوت ✅", url=f"https://t.me/{CHANNEL_ID}"))
        return bot.send_message(message.chat.id, f"⚠️ أهلاً {user_name}! اشترك بقناة البوت أولاً حتى يشتغل عندك الذكاء الاصطناعي والتحميل.", reply_markup=markup)
    
    bot.reply_to(message, f"هلا والله {user_name}! نورت بوت حسون AI 🚀\n\n🔹 أرسل أي سؤال (بالعراقي أو أي لغة) وسأجيبك فوراً.\n🔹 أرسل رابط فيديو (TikTok, Instagram, YouTube) لتحميله مباشرة.")

# --- نظام تحميل الفيديوهات ---
def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video_%(id)s.mp4',
        'quiet': True,
        'no_warnings': True,
        'max_filesize': 50 * 1024 * 1024 # حد أقصى 50 ميجا
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    if not is_subscribed(message.from_user.id): return
    
    url = message.text
    msg = bot.reply_to(message, "⏳ صار تدلل، جاري التحميل... انتظر ثواني.")
    
    try:
        video_file = download_video(url)
        with open(video_file, 'rb') as v:
            bot.send_video(message.chat.id, v, caption="✅ تم التحميل بواسطة حسون AI")
        os.remove(video_file) # حذف الملف لتوفير المساحة
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ عذراً، هذا الرابط غير مدعوم أو حجم الفيديو كبير جداً.", message.chat.id, msg.message_id)

# --- نظام الذكاء الاصطناعي (حسون AI) ---
@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    if not is_subscribed(message.from_user.id): return
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    user_query = message.text
    # توجيه البوت ليتحدث بلهجة عراقية بطلاقة
    prompt = f"أنت مساعد ذكي اسمك حسون AI. تتحدث بطلاقة وبشكل طبيعي جداً باللهجة العراقية. جاوب على: {user_query}"
    api_url = f"https://text.pollinations.ai/{prompt}?model=llama&search=true"
    
    # محاولة الاتصال 3 مرات لتفادي ضغط السيرفر
    for attempt in range(3):
        try:
            response = requests.get(api_url, timeout=20)
            if response.status_code == 200 and len(response.text) > 1:
                return bot.reply_to(message, response.text)
        except:
            time.sleep(1)
            continue
            
    bot.reply_to(message, "🤖 السيرفر تعبان شوية، ارجع اسألني هسة وراح أجاوبك فوراً!")

if __name__ == "__main__":
    print("البوت شغال بالتوكن الجديد... انطلق يا حسين!")
    bot.infinity_polling()
