"""
Telegram Bot implementation
"""
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)

from api.job_manager import job_manager
from api.processor import process_video
from api.models import JobStatus


class TelegramBot:
    """Telegram bot for video processing"""
    
    def __init__(self, token: str):
        self.token = token
        self.app: Optional[Application] = None
        self.user_settings: Dict[int, dict] = {}
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🎬 *YT Heatmap Clipper Bot*

Saya bisa membantu Anda membuat klip viral dari video YouTube berdasarkan data heatmap!

*Perintah yang tersedia:*
/clip <url> - Proses satu video
/batch <url1> <url2> ... - Proses beberapa video sekaligus
/settings - Atur preferensi
/status - Cek status pemrosesan
/help - Bantuan

*Cara pakai:*
1. Kirim link YouTube dengan /clip
2. Bot akan memproses video
3. Tunggu klip selesai dibuat
4. Download klip yang dihasilkan

Kirim /clip diikuti link YouTube untuk mulai!
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
*Bantuan YT Heatmap Clipper*

*Perintah:*
• /clip <url> - Proses video YouTube
• /batch <url1> <url2> - Proses beberapa video
• /settings - Atur crop mode, subtitle, dll
• /status - Lihat status job yang sedang berjalan

*Contoh:*
/clip https://youtube.com/watch?v=xxxxx
/batch https://youtube.com/watch?v=xxx https://youtube.com/watch?v=yyy

*Crop Modes:*
• none - Tanpa crop
• vertical - 9:16 (TikTok/Reels)
• square - 1:1 (Instagram)
• facecam_left - Fokus kiri (facecam)
• facecam_right - Fokus kanan (facecam)
• auto - Deteksi otomatis

*Tips:*
- Video dengan heatmap data akan menghasilkan klip terbaik
- Subtitle otomatis menggunakan Whisper AI
- Setiap klip maksimal 60 detik
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode="Markdown"
        )
    
    async def clip_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clip command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Gunakan: /clip <youtube_url>\n\n"
                "Contoh: /clip https://youtube.com/watch?v=xxxxx"
            )
            return
        
        url = context.args[0]
        user_id = update.effective_user.id
        
        # Get user settings or use defaults
        settings = self.user_settings.get(user_id, {
            "crop_mode": "none",
            "use_subtitle": True,
            "whisper_model": "small",
            "whisper_language": "id",
            "max_clips": 10,
            "min_score": 0.40
        })
        
        # Create job
        job_data = {
            "url": url,
            **settings
        }
        
        try:
            job_id = await job_manager.create_job(job_data)
            
            # Send initial message
            status_msg = await update.message.reply_text(
                f"⏳ Memproses video...\n\n"
                f"Job ID: `{job_id}`\n"
                f"Status: Queued",
                parse_mode="Markdown"
            )
            
            # Store message ID for updates
            context.user_data[f"job_{job_id}"] = {
                "chat_id": update.effective_chat.id,
                "message_id": status_msg.message_id
            }
            
            # Start processing
            asyncio.create_task(self._process_and_notify(job_id, job_data, context))
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def batch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Gunakan: /batch <url1> <url2> ...\n\n"
                "Contoh: /batch https://youtube.com/watch?v=xxx https://youtube.com/watch?v=yyy"
            )
            return
        
        urls = context.args
        user_id = update.effective_user.id
        
        settings = self.user_settings.get(user_id, {
            "crop_mode": "none",
            "use_subtitle": True,
            "whisper_model": "small",
            "whisper_language": "id",
            "max_clips": 10,
            "min_score": 0.40
        })
        
        await update.message.reply_text(
            f"⏳ Memproses {len(urls)} video...\n\n"
            "Anda akan menerima notifikasi untuk setiap video yang selesai."
        )
        
        for url in urls:
            job_data = {"url": url, **settings}
            
            try:
                job_id = await job_manager.create_job(job_data)
                asyncio.create_task(self._process_and_notify(job_id, job_data, context))
            
            except Exception as e:
                await update.message.reply_text(f"❌ Error untuk {url}: {str(e)}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = update.effective_user.id
        settings = self.user_settings.get(user_id, {
            "crop_mode": "none",
            "use_subtitle": True,
            "whisper_model": "small",
            "whisper_language": "id"
        })
        
        keyboard = [
            [
                InlineKeyboardButton("Crop: None", callback_data="crop_none"),
                InlineKeyboardButton("Crop: Vertical", callback_data="crop_vertical")
            ],
            [
                InlineKeyboardButton("Crop: Square", callback_data="crop_square"),
                InlineKeyboardButton("Crop: Auto", callback_data="crop_auto")
            ],
            [
                InlineKeyboardButton(
                    f"Subtitle: {'✅' if settings['use_subtitle'] else '❌'}",
                    callback_data="toggle_subtitle"
                )
            ],
            [
                InlineKeyboardButton("Model: Tiny", callback_data="model_tiny"),
                InlineKeyboardButton("Model: Small", callback_data="model_small"),
                InlineKeyboardButton("Model: Medium", callback_data="model_medium")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = f"""
⚙️ *Pengaturan Saat Ini*

Crop Mode: `{settings['crop_mode']}`
Subtitle: `{'Aktif' if settings['use_subtitle'] else 'Nonaktif'}`
Whisper Model: `{settings['whisper_model']}`
Bahasa: `{settings['whisper_language']}`

Klik tombol di bawah untuk mengubah:
        """
        
        await update.message.reply_text(
            settings_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # Get all jobs for this user (simplified - in production, track by user)
        active_jobs = [
            job for job in job_manager.jobs.values()
            if job["status"] in [JobStatus.QUEUED, JobStatus.PROCESSING]
        ]
        
        if not active_jobs:
            await update.message.reply_text("✅ Tidak ada job yang sedang berjalan")
            return
        
        status_text = "*Job yang sedang berjalan:*\n\n"
        
        for job in active_jobs[:5]:  # Show max 5
            status_text += (
                f"Job ID: `{job['job_id'][:8]}...`\n"
                f"Status: {job['status'].value}\n"
                f"Progress: {job['progress']:.1f}%\n"
                f"Clips: {job['clips_done']}/{job['total_clips']}\n\n"
            )
        
        await update.message.reply_text(status_text, parse_mode="Markdown")
    
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {
                "crop_mode": "none",
                "use_subtitle": True,
                "whisper_model": "small",
                "whisper_language": "id"
            }
        
        data = query.data
        
        if data.startswith("crop_"):
            self.user_settings[user_id]["crop_mode"] = data.replace("crop_", "")
        
        elif data == "toggle_subtitle":
            self.user_settings[user_id]["use_subtitle"] = not self.user_settings[user_id]["use_subtitle"]
        
        elif data.startswith("model_"):
            self.user_settings[user_id]["whisper_model"] = data.replace("model_", "")
        
        # Update message
        settings = self.user_settings[user_id]
        
        settings_text = f"""
⚙️ *Pengaturan Saat Ini*

Crop Mode: `{settings['crop_mode']}`
Subtitle: `{'Aktif' if settings['use_subtitle'] else 'Nonaktif'}`
Whisper Model: `{settings['whisper_model']}`
Bahasa: `{settings['whisper_language']}`

✅ Pengaturan disimpan!
        """
        
        await query.edit_message_text(settings_text, parse_mode="Markdown")
    
    async def _process_and_notify(
        self, 
        job_id: str, 
        job_data: dict, 
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Process video and send notifications"""
        # Start processing
        await process_video(job_id, job_data)
        
        # Get job result
        job = job_manager.get_job(job_id)
        
        if not job:
            return
        
        # Get chat info
        job_info = context.user_data.get(f"job_{job_id}")
        if not job_info:
            return
        
        chat_id = job_info["chat_id"]
        
        if job["status"] == JobStatus.COMPLETED:
            # Send success message
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Selesai! {len(job['clips'])} klip berhasil dibuat."
            )
            
            # Send each clip as video
            for clip in job["clips"]:
                clip_path = Path("clips") / clip["filename"]
                
                if clip_path.exists():
                    caption = f"📹 {clip.get('title', 'Clip')}\n\n"
                    if clip.get("description"):
                        caption += f"{clip['description'][:200]}..."
                    
                    try:
                        with open(clip_path, "rb") as video_file:
                            await context.bot.send_video(
                                chat_id=chat_id,
                                video=video_file,
                                caption=caption,
                                supports_streaming=True
                            )
                    except Exception as e:
                        print(f"Error sending video: {e}")
        
        elif job["status"] == JobStatus.FAILED:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Gagal memproses video\n\nError: {job.get('error', 'Unknown error')}"
            )
    
    async def start(self):
        """Start the bot"""
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("clip", self.clip_command))
        self.app.add_handler(CommandHandler("batch", self.batch_command))
        self.app.add_handler(CommandHandler("settings", self.settings_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CallbackQueryHandler(self.settings_callback))
        
        # Start polling
        print("🤖 Telegram bot started")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            print("🤖 Telegram bot stopped")


async def run_bot(token: str):
    """Run the Telegram bot"""
    bot = TelegramBot(token)
    await bot.start()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await bot.stop()
