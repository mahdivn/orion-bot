import os
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ChatMemberStatus
import yt_dlp

# ========== تنظیمات اولیه ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== گرفتن تنظیمات از Environment Variables ==========
TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/mvn_vpn")

if not TOKEN:
    logger.error("❌ BOT_TOKEN تنظیم نشده!")
if not REQUIRED_CHANNEL_ID:
    logger.error("❌ REQUIRED_CHANNEL_ID تنظیم نشده!")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# لینک کانال (برای استفاده در جاهای مختلف)
CHANNEL_USERNAME = "@mvn_vpn"
CHANNEL_URL = "https://t.me/mvn_vpn"

# ========== توابع کمکی ==========
def is_instagram_link(url: str) -> bool:
    patterns = [
        r'(https?://)?(www\.)?instagram\.com/(p|reel|tv|stories)/.+',
        r'(https?://)?(www\.)?instagr\.am/(p|reel|tv|stories)/.+'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

async def is_member(user_id: int, context) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

async def check_join_required(update: Update, context) -> bool:
    user_id = update.effective_user.id
    
    if await is_member(user_id, context):
        return True
    
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔒 **برای استفاده از ربات، ابتدا عضو کانال ما شوید!**\n\n"
        f"🎁 **کانال {CHANNEL_USERNAME}**\n"
        "📡 **دریافت کانفیگ و پروکسی رایگان**\n"
        "⚡ **به‌روزترین سرورها | لینک مستقیم**\n\n"
        "👇 **روی دکمه زیر کلیک کنید** 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return False

# ========== دستورات ربات ==========
async def start(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    keyboard = [
        [InlineKeyboardButton("🆘 راهنما", callback_data="help")],
        [InlineKeyboardButton("📥 نحوه دریافت لینک", callback_data="tutorial")],
        [InlineKeyboardButton("🎁 کانال ما", url=CHANNEL_URL)],
        [InlineKeyboardButton("⭐ پشتیبانی", url=CHANNEL_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌌 **به Orion خوش آمدید!**\n\n"
        "🤖 ربات قدرتمند دانلود از اینستاگرام\n\n"
        "📥 **کافیست لینک پست، ریلز یا استوری را بفرستید**\n"
        "تا در سریعترین زمان دانلود شود.\n\n"
        f"🎁 **برای دریافت کانفیگ و پروکسی رایگان:**\n"
        f"📢 {CHANNEL_USERNAME}\n\n"
        "✨ **سریع | ساده | حرفه‌ای**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "🆘 **راهنمای استفاده از Orion**\n\n"
        "📌 کافیست لینک اینستاگرام را بفرستید\n"
        "مثال:\n"
        "`https://www.instagram.com/p/Cxample123/`\n\n"
        "📥 **قابلیت‌ها:**\n"
        "✅ دانلود پست\n"
        "✅ دانلود ریلز\n"
        "✅ دانلود استوری\n"
        "✅ کیفیت اصلی\n\n"
        "⚡ فقط لینک بدهید، بقیه با من 🌌",
        parse_mode='Markdown'
    )

async def download_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "📥 **آموزش دریافت لینک از اینستاگرام**\n\n"
        "1️⃣ داخل اینستاگرام باز کنید\n"
        "2️⃣ روی سه نقطه ⋮ بزنید\n"
        "3️⃣ **Copy Link** را انتخاب کنید\n"
        "4️⃣ لینک را اینجا بچسبانید و بفرستید\n\n"
        "✨ من خودکار دانلود می‌کنم!",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "🌌 **درباره Orion**\n\n"
        "🆔 نام: Orion Downloader\n"
        "📅 نسخه: 3.0.0\n"
        "💻 ساخته شده با: Python + yt-dlp\n\n"
        "🎁 **کانال ما:**\n"
        f"{CHANNEL_USERNAME}\n"
        f"{CHANNEL_URL}\n\n"
        "⭐ اگر راضی هستید، ما را معرفی کنید!",
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_membership":
        user_id = query.from_user.id
        if await is_member(user_id, context):
            await query.edit_message_text(
                "✅ **عضویت شما تایید شد!**\n\n"
                "🎉 به جمع ما خوش آمدید\n"
                "اکنون می‌توانید از ربات استفاده کنید.\n\n"
                f"📢 {CHANNEL_USERNAME}\n"
                "🌌 Orion در خدمت شماست",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **هنوز عضو کانال نشده‌اید!**\n\n"
                "🔰 روی دکمه زیر بزنید و عضو شوید\n"
                f"🎁 {CHANNEL_USERNAME}\n\n"
                "👇👇👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)]
                ])
            )
    
    elif query.data == "help":
        await query.edit_message_text(
            "🆘 **راهنمای استفاده**\n\n"
            "📌 لینک اینستاگرام را بفرستید\n"
            "مثال:\n"
            "`https://www.instagram.com/p/Cxample123/`\n\n"
            "✅ قابلیت‌ها:\n"
            "• دانلود پست\n"
            "• دانلود ریلز\n"
            "• دانلود استوری",
            parse_mode='Markdown'
        )
    elif query.data == "tutorial":
        await query.edit_message_text(
            "📥 **آموزش گرفتن لینک**\n\n"
            "1️⃣ روی سه نقطه ⋮ بزنید\n"
            "2️⃣ Copy Link را انتخاب کنید\n"
            "3️⃣ لینک را بفرستید\n\n"
            "⚠️ فقط محتوای **عمومی** قابل دانلود است.",
            parse_mode='Markdown'
        )

async def download_instagram(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    url = update.message.text.strip()
    
    if not is_instagram_link(url):
        await update.message.reply_text(
            "❌ **لینک معتبر نیست**\n\n"
            "📌 فقط لینک اینستاگرام ارسال کنید\n"
            "`https://www.instagram.com/p/...`",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        "⏳ **در حال پردازش...**\n\n"
        "🌌 Orion در حال یافتن فایل شماست",
        parse_mode='Markdown'
    )
    
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s_%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        await status_msg.edit_text(
            "📥 **در حال دریافت اطلاعات...**\n\n"
            "🔗 اتصال به اینستاگرام",
            parse_mode='Markdown'
        )
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                import glob
                files = glob.glob(f"{DOWNLOAD_DIR}/*{info.get('id', '')}*")
                filename = files[0] if files else None
            
            if not filename or not os.path.exists(filename):
                raise Exception("فایل دانلود نشد")
        
        file_size = os.path.getsize(filename) / (1024 * 1024)
        if file_size > 50:
            await status_msg.edit_text(
                f"❌ **حجم فایل زیاد است**\n\n"
                f"📦 حجم: {file_size:.1f} مگابایت\n"
                f"⚠️ حد مجاز تلگرام: ۵۰ مگابایت",
                parse_mode='Markdown'
            )
            os.remove(filename)
            return
        
        await status_msg.edit_text(
            "📤 **در حال ارسال به تلگرام...**",
            parse_mode='Markdown'
        )
        
        caption_text = (
            "✅ **دانلود شد!**\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 **{CHANNEL_USERNAME}**\n"
            "📡 **کانال کانفیگ و پروکسی رایگان**\n"
            "⚡ **به‌روزترین سرورها | لینک مستقیم**\n\n"
            f"🔗 {CHANNEL_URL}\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🌌 Orion | اینستاگرام"
        )
        
        mime_type = filename.split('.')[-1].lower()
        with open(filename, 'rb') as media_file:
            if mime_type in ['mp4', 'mov', 'avi']:
                await update.message.reply_video(
                    video=media_file,
                    caption=caption_text,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_document(
                    document=media_file,
                    caption=caption_text,
                    parse_mode='Markdown'
                )
        
        os.remove(filename)
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text(
            "❌ **خطا در دانلود**\n\n"
            "📌 دلایل احتمالی:\n"
            "• لینک خصوصی است\n"
            "• لینک نامعتبر است\n"
            "• محدودیت اینستاگرام\n\n"
            "✨ لینک دیگری امتحان کنید",
            parse_mode='Markdown'
        )

# ========== اجرای اصلی ==========
def main():
    if not TOKEN:
        logger.error("❌ توکن پیدا نشد!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("download", download_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    
    logger.info("🌌 Orion Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
