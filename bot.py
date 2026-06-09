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
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

if not TOKEN:
    logger.error("❌ BOT_TOKEN تنظیم نشده!")
if not REQUIRED_CHANNEL_ID:
    logger.error("❌ REQUIRED_CHANNEL_ID تنظیم نشده!")
if not CHANNEL_LINK:
    logger.error("❌ CHANNEL_LINK تنظیم نشده!")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
        [InlineKeyboardButton("📢 جوین شدن در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔒 **دسترسی محدود!**\n\n"
        "برای استفاده از ربات اوریون، ابتدا باید در کانال ما عضو بشی.\n\n"
        "👇 روی دکمه زیر بزن و جوین شو، بعد بزن **عضو شدم**\n\n"
        "🌌 **اوریون - شکارچی اینستاگرام**",
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
        [InlineKeyboardButton("🌌 کانال اوریون", url=CHANNEL_LINK)],
        [InlineKeyboardButton("⭐ پشتیبانی", url=CHANNEL_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌌 **به اوریون خوش اومدی**\n\n"
        "ربات قدرتمند دانلود از اینستاگرام 🚀\n\n"
        "📥 کافیه لینک پست، ریلز یا استوری رو برام بفرستی\n"
        "تا در سریع‌ترین زمان با کیفیت بالا برات دانلود کنم.\n\n"
        "✨ **سریع | ساده | حرفه‌ای**",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "🆘 **راهنمای استفاده از اوریون**\n\n"
        "📌 فقط کافیه لینک اینستاگرام رو بفرستی\n"
        "مثلاً:\n"
        "`https://www.instagram.com/p/Cxample123/`\n\n"
        "📥 **قابلیت‌ها:**\n"
        "• دانلود پست\n"
        "• دانلود ریلز\n"
        "• دانلود استوری\n"
        "• دریافت با کیفیت بالا\n\n"
        "⚡ بدون نیاز به هیچ تنظیمات اضافه\n"
        "فقط لینک بده، بقیه‌ش با من 🌌",
        parse_mode='Markdown'
    )

async def download_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "📥 **چطور لینک بفرستم؟**\n\n"
        "1️⃣ داخل اینستاگرام باز کن\n"
        "2️⃣ روی سه نقطه ⋮ بزن\n"
        "3️⃣ **Copy Link** رو انتخاب کن\n"
        "4️⃣ بیا اینجا و لینک رو بچسبون و بفرست\n\n"
        "✨ من خودکار دانلود می‌کنم و برات می‌فرستم!",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context):
    if not await check_join_required(update, context):
        return
    
    await update.message.reply_text(
        "🌌 **درباره اوریون**\n\n"
        "🆔 **نام:** Orion Downloader\n"
        "📅 **نسخه:** 2.0.0\n"
        "💻 **ساخته شده با:** Python + yt-dlp\n\n"
        "🎯 **هدف:** سریع‌ترین و ساده‌ترین ربات دانلود از اینستاگرام\n\n"
        "⭐ اگه از اوریون راضی هستی، به دوستات هم معرفی کن!",
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_membership":
        user_id = query.from_user.id
        if await is_member(user_id, context):
            await query.edit_message_text(
                "✅ **تبریک!**\n\n"
                "تو عضویت رو تأیید کردی.\n"
                "حالا می‌تونی از ربات استفاده کنی.\n\n"
                "🌌 **اوریون در خدمت توست**",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ **هنوز عضو نشدی!**\n\n"
                "اول روی دکمه زیر بزن و عضو شو، بعد دوباره **عضو شدم** رو بزن.\n\n"
                "👇 **جوین شو:**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 جوین شدن در کانال", url=CHANNEL_LINK)]
                ])
            )
    
    elif query.data == "help":
        await query.edit_message_text(
            "🆘 **راهنمای استفاده از اوریون**\n\n"
            "📌 فقط کافیه لینک اینستاگرام رو بفرستی\n"
            "مثلاً:\n"
            "`https://www.instagram.com/p/Cxample123/`\n\n"
            "📥 **قابلیت‌ها:**\n"
            "• دانلود پست\n"
            "• دانلود ریلز\n"
            "• دانلود استوری\n"
            "• دریافت با کیفیت بالا\n\n"
            "⚡ بدون نیاز به هیچ تنظیمات اضافه\n"
            "فقط لینک بده، بقیه‌ش با من 🌌",
            parse_mode='Markdown'
        )
    elif query.data == "tutorial":
        await query.edit_message_text(
            "📥 **آموزش گرفتن لینک از اینستاگرام**\n\n"
            "**مراحل:**\n\n"
            "1️⃣ روی سه نقطه ⋮ بالای پست بزن\n"
            "2️⃣ گزینه **Copy Link** رو انتخاب کن\n"
            "3️⃣ برگرد به اینجا و لینک رو بچسبون\n"
            "4️⃣ بفرست برام!\n\n"
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
            "📌 لطفاً فقط لینک اینستاگرام ارسال کن\n"
            "مثلاً پست، ریلز یا استوری\n\n"
            "✨ مثلاً:\n"
            "`https://www.instagram.com/p/Cxample123/`",
            parse_mode='Markdown'
        )
        return
    
    status_msg = await update.message.reply_text(
        "⏳ **در حال پردازش لینک...**\n\n"
        "🌌 اوریون در حال استخراج فایل است\n"
        "لطفاً چند لحظه صبر کن 🚀",
        parse_mode='Markdown'
    )
    
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s_%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
        }
        
        await status_msg.edit_text(
            "📥 **در حال دریافت اطلاعات...**\n\n"
            "🌌 اوریون در حال اتصال به اینستاگرام 🔗",
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
                f"📦 حجم فایل: {file_size:.1f} مگابایت\n"
                f"⚠️ حد مجاز تلگرام: ۵۰ مگابایت\n\n"
                "لطفاً لینک دیگری امتحان کن.",
                parse_mode='Markdown'
            )
            os.remove(filename)
            return
        
        await status_msg.edit_text(
            "📤 **در حال ارسال به تلگرام...**\n\n"
            "🌌 اوریون فایل رو برات می‌فرسته ✈️",
            parse_mode='Markdown'
        )
        
        mime_type = filename.split('.')[-1].lower()
        with open(filename, 'rb') as media_file:
            if mime_type in ['mp4', 'mov', 'avi']:
                await update.message.reply_video(
                    video=media_file,
                    caption="✅ **دانلود شد!**\n\n🌌 اوریون | شکارچی اینستاگرام",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_document(
                    document=media_file,
                    caption="✅ **دانلود شد!**\n\n🌌 اوریون | شکارچی اینستاگرام",
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
            "✨ یک لینک دیگه امتحان کن.",
            parse_mode='Markdown'
        )

# ========== اجرای اصلی ==========
def main():
    if not TOKEN:
        logger.error("❌ توکن پیدا نشد! متغیر BOT_TOKEN رو در رندر تنظیم کن.")
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