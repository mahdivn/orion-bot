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

# 👇✅ اینجا درسته: mvn_vpn (با آندرلاین)
CHANNEL_USERNAME = "@mvn_vpn"
CHANNEL_URL = "https://t.me/mvn_vpn"

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

async def start(update: Update, context):
    user_id = update.effective_user.id
    
    if not await is_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔒 **دسترسی محدود!** 🔒\n\n"
            "برای استفاده از ربات **Orion**، ابتدا باید در کانال ما عضو شوید.\n\n"
            f"📢 **کانال:** {CHANNEL_USERNAME}\n"
            "🎁 **مزیت عضویت:**\n"
            "• کانفیگ و پروکسی رایگان\n"
            "• به‌روزترین سرورها\n"
            "• لینک مستقیم و بدون فیلتر\n\n"
            "👇 **روی دکمه زیر بزنید و عضو شوید** 👇",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🆘 راهنما", callback_data="help")],
        [InlineKeyboardButton("📥 نحوه دریافت لینک", callback_data="tutorial")],
        [InlineKeyboardButton("🎁 کانال ما", url=CHANNEL_URL)],
        [InlineKeyboardButton("⭐ پشتیبانی", url=CHANNEL_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌌✨ **به ربات Orion خوش آمدید!** ✨🌌\n\n"
        "═══════════════════════════\n"
        "🤖 **ربات قدرتمند دانلود از اینستاگرام**\n"
        "═══════════════════════════\n\n"
        "📥 **قابلیت‌های من:**\n"
        "✅ دانلود پست‌های اینستاگرام\n"
        "✅ دانلود ریلز (Reels)\n"
        "✅ دانلود استوری‌ها\n"
        "✅ کیفیت اصلی و بدون کاهش\n"
        "✅ سرعت بالا و رایگان\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **نحوه استفاده:**\n"
        "🔹 فقط کافیست لینک پست، ریلز یا استوری اینستاگرام را برای من بفرستید\n"
        "🔹 من در سریع‌ترین زمان فایل را دانلود و برای شما ارسال می‌کنم\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 **کانال کانفیگ و پروکسی رایگان:**\n"
        f"📢 {CHANNEL_USERNAME}\n\n"
        "✨ **سریع · ساده · حرفه‌ای** ✨\n\n"
        "👇 **از دکمه‌های زیر استفاده کنید** 👇",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 **دسترسی محدود!**\n\nبرای استفاده از راهنما، ابتدا عضو کانال شوید.",
            reply_markup=reply_markup
        )
        return
    
    await update.message.reply_text(
        "🆘 **راهنمای استفاده از Orion**\n\n"
        "📌 **مراحل کار:**\n"
        "1️⃣ لینک پست اینستاگرام را کپی کنید\n"
        "2️⃣ لینک را برای من بفرستید\n"
        "3️⃣ فایل دانلود شده را دریافت کنید\n\n"
        "📥 **لینک‌های پشتیبانی شده:**\n"
        "• پست‌های معمولی\n"
        "• ریلز (Reels)\n"
        "• استوری‌ها\n\n"
        "⚠️ **نکته:** فقط محتوای **عمومی** قابل دانلود است.\n\n"
        "⚡ فقط لینک بدهید، بقیه با من 🌌",
        parse_mode='Markdown'
    )

async def download_command(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 **دسترسی محدود!**\n\nبرای استفاده از ربات، ابتدا عضو کانال شوید.",
            reply_markup=reply_markup
        )
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
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 **دسترسی محدود!**\n\nبرای اطلاعات بیشتر، ابتدا عضو کانال شوید.",
            reply_markup=reply_markup
        )
        return
    
    await update.message.reply_text(
        "🌌 **درباره Orion**\n\n"
        "🆔 **نام:** Orion Downloader\n"
        "📅 **نسخه:** 3.0.0\n"
        "💻 **ساخته شده با:** Python + yt-dlp\n\n"
        "🎯 **هدف:** سریع‌ترین ربات دانلود از اینستاگرام\n\n"
        f"🎁 **کانال ما:**\n"
        f"{CHANNEL_USERNAME}\n\n"
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
                "✅ **عضویت شما تأیید شد!**\n\n"
                "🎉 به جمع ما خوش آمدید\n\n"
                "🌌 **دستور /start را بزنید تا ربات را استارت کنید**",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **هنوز عضو کانال نشده‌اید!**\n\n"
                "🔰 روی دکمه زیر بزنید و عضو شوید\n\n"
                f"🎁 **کانال:** {CHANNEL_USERNAME}\n\n"
                "👇👇👇",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)]
                ])
            )
    
    elif query.data == "help":
        await query.edit_message_text(
            "🆘 **راهنمای استفاده از Orion**\n\n"
            "📌 **مراحل کار:**\n"
            "1️⃣ لینک پست اینستاگرام را کپی کنید\n"
            "2️⃣ لینک را برای من بفرستید\n"
            "3️⃣ فایل دانلود شده را دریافت کنید\n\n"
            "📥 **لینک‌های پشتیبانی شده:**\n"
            "• پست‌های معمولی\n"
            "• ریلز (Reels)\n"
            "• استوری‌ها\n\n"
            "⚠️ فقط محتوای **عمومی** قابل دانلود است.",
            parse_mode='Markdown'
        )
    elif query.data == "tutorial":
        await query.edit_message_text(
            "📥 **آموزش گرفتن لینک از اینستاگرام**\n\n"
            "1️⃣ روی سه نقطه ⋮ بالای پست بزنید\n"
            "2️⃣ گزینه **Copy Link** را انتخاب کنید\n"
            "3️⃣ برگردید به اینجا و لینک را بچسبانید\n"
            "4️⃣ بفرستید برای من!\n\n"
            "⚠️ فقط محتوای **عمومی** قابل دانلود است.",
            parse_mode='Markdown'
        )

async def download_instagram(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_URL)],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 **دسترسی محدود!**\n\nبرای دانلود، ابتدا عضو کانال شوید.",
            reply_markup=reply_markup
        )
        return
    
    url = update.message.text.strip()
    
    if not is_instagram_link(url):
        await update.message.reply_text(
            "❌ **لینک معتبر نیست**\n\n"
            "📌 فقط لینک اینستاگرام ارسال کنید\n"
            "مثال:\n"
            "`https://www.instagram.com/p/Cxample123/`",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        "⏳ **در حال پردازش...**\n\n"
        "🌌 Orion در حال یافتن فایل شماست 🚀",
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
            "📤 **در حال ارسال به تلگرام...**\n\n"
            "✈️ لحظاتی دیگر ارسال می‌شود",
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
            "🌌 **Orion**"
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
            "📌 **دلایل احتمالی:**\n"
            "• لینک خصوصی است (پیج خصوصی)\n"
            "• لینک نامعتبر یا حذف شده\n"
            "• اینستاگرام محدودیت ایجاد کرده\n\n"
            "✨ یک لینک دیگر امتحان کنید.",
            parse_mode='Markdown'
        )

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
    app.run_polling()

if __name__ == "__main__":
    main()
