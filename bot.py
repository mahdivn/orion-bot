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
    CHANNEL_LINK = "https://t.me/mvn_vpn"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
            [InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")],
            [InlineKeyboardButton("✅ عضو شدم", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔒 **برای استفاده از ربات، ابتدا عضو کانال شوید:**\n\n📢 @mvn_vpn",
            reply_markup=reply_markup
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🆘 راهنما", callback_data="help")],
        [InlineKeyboardButton("📥 آموزش دریافت لینک", callback_data="tutorial")],
        [InlineKeyboardButton("🎁 کانال ما", url="https://t.me/mvn_vpn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌌 **به ربات Orion خوش آمدید!**\n\n"
        "📥 لینک اینستاگرام را بفرستید تا فایل را دانلود کنم.\n\n"
        "🎁 @mvn_vpn",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")]]
        await update.message.reply_text("🔒 ابتدا عضو کانال شوید: @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text(
        "🆘 **راهنما:**\n"
        "لینک اینستاگرام را بفرستید تا دانلود کنم.\n"
        "پشتیبانی: @mvn_vpn"
    )

async def download_command(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")]]
        await update.message.reply_text("🔒 ابتدا عضو کانال شوید: @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text("📥 لینک اینستاگرام را بفرستید تا دانلود کنم.")

async def about_command(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")]]
        await update.message.reply_text("🔒 ابتدا عضو کانال شوید: @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text(
        "🌌 **Orion Downloader**\n"
        "ربات دانلود از اینستاگرام\n"
        "🎁 @mvn_vpn"
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "check_membership":
        if await is_member(user_id, context):
            await query.edit_message_text("✅ عضویت تأیید شد! حالا /start را بزنید.")
        else:
            await query.edit_message_text(
                "❌ هنوز عضو نشدید!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")]])
            )
    elif query.data == "help":
        await query.edit_message_text("🆘 لینک اینستاگرام را بفرستید.")
    elif query.data == "tutorial":
        await query.edit_message_text(
            "📥 **آموزش دریافت لینک:**\n"
            "1. روی سه نقطه ⋮ بالای پست بزنید\n"
            "2. Copy Link را انتخاب کنید\n"
            "3. لینک را اینجا بفرستید"
        )

async def download_instagram(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")]]
        await update.message.reply_text("🔒 ابتدا عضو کانال شوید: @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    url = update.message.text.strip()
    if not is_instagram_link(url):
        await update.message.reply_text("❌ لینک اینستاگرام معتبر نیست.\nمثال: https://www.instagram.com/p/...")
        return
    
    status_msg = await update.message.reply_text("⏳ در حال دانلود...")
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s_%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                import glob
                files = glob.glob(f"{DOWNLOAD_DIR}/*{info.get('id', '')}*")
                filename = files[0] if files else None
            if not filename:
                raise Exception("فایل پیدا نشد")
        
        # کپشن با لینک درست
        caption = (
            "✅ **دانلود شد!**\n\n"
            "🎁 **کانال کانفیگ و پروکسی رایگان:**\n"
            "📢 @mvn_vpn\n\n"
            "🔗 https://t.me/mvn_vpn\n\n"
            "🌌 Orion"
        )
        
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption=caption, parse_mode='Markdown')
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        logger.error(e)
        await status_msg.edit_text("❌ خطا در دانلود. لطفاً لینک دیگری امتحان کنید.")

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
