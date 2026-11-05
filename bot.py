import os
import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Ambil konfigurasi dari Environment Variables Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "rahasia12345") # Ganti dengan kata acak kamu sendiri

# 2. Konfigurasi ID (GANTI DENGAN DATA KAMU)
ID_CH_UTAMA = -1001234567890  
ID_GC_DISKUSI = -1009876543210 

# 3. Database PJ (GANTI DENGAN DATA KAMU)
DATABASE_PJ = {
    111111111: { 
        "nama_series": "Judul Series A",
        "cover_url": "https://telegra.ph/file/contoh.jpg", 
        "link_gc": "https://t.me/gcpdfa",
        "link_series": "https://t.me/seriesa"
    }
}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot PDF Updater Aktif! 🚀")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    user_id = update.message.from_user.id
    file_name = document.file_name
    
    if user_id not in DATABASE_PJ:
        return # Diamkan jika bukan PJ terdaftar

    data_pj = DATABASE_PJ[user_id]
    match = re.search(r'(?:ch|chapter|ep|episode)\s*\.?\s*(\d+)', file_name, re.IGNORECASE)
    nomor_episode = match.group(1) if match else "???"

    caption = f"📖 *{data_pj['nama_series']}*\n\n"
    caption += f"📌 Update : Episode {nomor_episode}\n\n"
    caption += f"🔗 [Join GC PDF]({data_pj['link_gc']}) | [Lihat Series]({data_pj['link_series']})"

    try:
        await context.bot.send_photo(
            chat_id=ID_CH_UTAMA,
            photo=data_pj['cover_url'],
            caption=caption,
            parse_mode='Markdown'
        )
        await update.message.reply_text(f"✅ Update Episode {nomor_episode} berhasil diposting!")
    except Exception as e:
        logging.error(f"Error kirim: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Chat(ID_GC_DISKUSI) & filters.Document.PDF, handle_pdf))

    # Jalankan sebagai Webhook agar kompatibel dengan Render Free Tier
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        secret_token=SECRET_TOKEN
    )

if __name__ == "__main__":
    main()
