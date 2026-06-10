import os
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ChatMemberStatus
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
REQUIRED_CHANNEL_ID = os.getenv("REQUIRED_CHANNEL_ID")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_instagram_link(url: str) -> bool:
    patterns = [r'(https?://)?(www\.)?instagram\.com/(p|reel|tv|stories)/.+', r'(https?://)?(www\.)?instagr\.am/(p|reel|tv|stories)/.+']
    return any(re.match(pattern, url) for pattern in patterns)

async def is_member(user_id: int, context) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def start(update: Update, context):
    user_id = update.effective_user.id
    if not await is_member(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/mvn_vpn")], [InlineKeyboardButton("✅ عضو شدم", callback_data="check")]]
        await update.message.reply_text("🔒 برای استفاده از ربات، ابتدا عضو کانال شوید:\n\n📢 @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    keyboard = [[InlineKeyboardButton("🎁 کانال ما", url="https://t.me/mvn_vpn")], [InlineKeyboardButton("🆘 راهنما", callback_data="help")]]
    await update.message.reply_text("🌌 به ربات Orion خوش آمدید!\n\nلینک اینستاگرام را بفرستید تا دانلود کنم.\n\n🎁 @mvn_vpn", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "check":
        if await is_member(query.from_user.id, context):
            await query.edit_message_text("✅ عضویت تایید شد! حالا /start را بزنید.")
        else:
            await query.edit_message_text("❌ هنوز عضو نشدید!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 عضویت", url="https://t.me/mvn_vpn")]]))
    elif query.data == "help":
        await query.edit_message_text("لینک اینستاگرام را بفرستید تا دانلود کنم.\n\n🎁 @mvn_vpn")

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
    msg = await update.message.reply_text("⏳ در حال دانلود...")
    try:
        ydl_opts = {'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s_%(id)s.%(ext)s'), 'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                import glob
                files = glob.glob(f"{DOWNLOAD_DIR}/*{info.get('id', '')}*")
                filename = files[0] if files else None
            if not filename:
                raise Exception("")
        caption = "✅ دانلود شد!\n\n🎁 @mvn_vpn\n🔗 https://t.me/mvn_vpn\n\n🌌 Orion"
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption=caption)
        os.remove(filename)
        await msg.delete()
    except:
        await msg.edit_text("❌ خطا در دانلود. لطفا لینک دیگری امتحان کنید.")

def main():
    if not TOKEN:
        logger.error("❌ توکن پیدا نشد!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    logger.info("🌌 Orion Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
