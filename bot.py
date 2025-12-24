import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from pydub import AudioSegment
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Maximum file size in bytes (45MB to be safe under Telegram's 50MB limit)
MAX_FILE_SIZE = 45 * 1024 * 1024

# Temporary directory for downloads
TEMP_DIR = Path('./temp_downloads')
TEMP_DIR.mkdir(exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎵 Welcome to YouTube Audio Converter Bot!\n\n"
        "Send me a YouTube URL and I'll convert it to audio for you.\n\n"
        "Just paste the link and I'll handle the rest! 🎧"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "📖 How to use:\n\n"
        "1. Send me any YouTube video URL\n"
        "2. Wait while I process it\n"
        "3. Receive your audio file(s)\n\n"
        "Note: Large videos will be split into multiple parts (under 45MB each)"
    )
    await update.message.reply_text(help_text)


def is_youtube_url(url: str) -> bool:
    """Check if the URL is a valid YouTube URL."""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)


def get_video_info(url: str) -> dict:
    """Get video information without downloading."""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Unknown'),
            'channel': info.get('uploader', 'Unknown'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', None)
        }


def download_audio(url: str, output_path: str) -> str:
    """Download YouTube video as audio."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return f"{output_path}.mp3"


def split_audio(file_path: str, max_size: int) -> list:
    """Split audio file into parts if it exceeds max_size."""
    file_size = os.path.getsize(file_path)
    
    if file_size <= max_size:
        return [file_path]
    
    # Load audio file
    audio = AudioSegment.from_mp3(file_path)
    duration_ms = len(audio)
    
    # Calculate number of parts needed
    num_parts = (file_size // max_size) + 1
    part_duration = duration_ms // num_parts
    
    parts = []
    base_name = file_path.rsplit('.', 1)[0]
    
    for i in range(num_parts):
        start = i * part_duration
        end = start + part_duration if i < num_parts - 1 else duration_ms
        
        part_audio = audio[start:end]
        part_path = f"{base_name}_part{i+1}.mp3"
        part_audio.export(part_path, format='mp3', bitrate='192k')
        parts.append(part_path)
    
    # Remove original file
    os.remove(file_path)
    
    return parts


async def download_thumbnail(url: str, output_path: str) -> str:
    """Download video thumbnail."""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(output_path, 'wb') as f:
                        f.write(await resp.read())
                    return output_path
    except Exception as e:
        logger.error(f"Error downloading thumbnail: {e}")
    
    return None


async def process_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process YouTube URL and convert to audio."""
    url = update.message.text.strip()
    
    # Validate URL
    if not is_youtube_url(url):
        await update.message.reply_text(
            "❌ Invalid URL. Please send a valid YouTube link."
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("⏳ Processing your request...")
    
    try:
        # Get video info
        await processing_msg.edit_text("📥 Fetching video information...")
        video_info = get_video_info(url)
        
        # Download audio
        await processing_msg.edit_text("⬇️ Downloading audio...")
        user_id = update.message.from_user.id
        output_path = TEMP_DIR / f"{user_id}_{video_info['title'][:50]}"
        audio_file = download_audio(url, str(output_path))
        
        # Convert and split if necessary
        await processing_msg.edit_text("🎵 Converting audio...")
        audio_parts = split_audio(audio_file, MAX_FILE_SIZE)
        
        # Download thumbnail
        thumbnail_path = None
        if video_info['thumbnail']:
            thumbnail_path = TEMP_DIR / f"{user_id}_thumb.jpg"
            thumbnail_path = await download_thumbnail(
                video_info['thumbnail'], 
                str(thumbnail_path)
            )
        
        # Send audio file(s)
        await processing_msg.edit_text(f"📤 Sending audio... ({len(audio_parts)} part(s))")
        
        for i, part in enumerate(audio_parts):
            caption = f"🎵 {video_info['title']}"
            if len(audio_parts) > 1:
                caption += f"\n📦 Part {i+1}/{len(audio_parts)}"
            caption += f"\n👤 {video_info['channel']}"
            
            with open(part, 'rb') as audio:
                if thumbnail_path and os.path.exists(thumbnail_path):
                    with open(thumbnail_path, 'rb') as thumb:
                        await update.message.reply_audio(
                            audio=audio,
                            thumbnail=thumb,
                            caption=caption,
                            title=video_info['title'],
                            performer=video_info['channel'],
                            duration=video_info['duration'] // len(audio_parts) if len(audio_parts) > 1 else video_info['duration']
                        )
                else:
                    await update.message.reply_audio(
                        audio=audio,
                        caption=caption,
                        title=video_info['title'],
                        performer=video_info['channel'],
                        duration=video_info['duration'] // len(audio_parts) if len(audio_parts) > 1 else video_info['duration']
                    )
            
            # Clean up part file
            os.remove(part)
        
        # Clean up thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        # Delete processing message
        await processing_msg.delete()
        
    except yt_dlp.utils.DownloadError as e:
        await processing_msg.edit_text(
            "❌ Error: Unable to download this video.\n"
            "It might be age-restricted, private, or unavailable."
        )
        logger.error(f"Download error: {e}")
    except Exception as e:
        await processing_msg.edit_text(
            "❌ An error occurred while processing your request.\n"
            "Please try again later or with a different video."
        )
        logger.error(f"Error processing URL: {e}")


def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_youtube_url))
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()