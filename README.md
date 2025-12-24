# YouTube Audio Converter Telegram Bot

A simple Telegram bot that converts YouTube videos to audio files (MP3 format at 192kbps) with metadata including title, channel name, and thumbnail.

## Features

-   ✅ Converts YouTube videos to MP3 audio (192kbps)
-   ✅ Includes metadata (title, artist/channel, thumbnail)
-   ✅ Auto-splits large files into parts under 45MB
-   ✅ Progress updates during conversion
-   ✅ Simple and user-friendly
-   ✅ **Works with Python 3.13+ (latest version)**
-   ✅ **No pydub dependency** - uses ffmpeg directly for better performance

## Requirements

-   Python 3.13+
-   FFmpeg (for audio conversion)
-   Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Project Structure

```
youtube_audio_bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version specification
├── render.yaml         # Render.com configuration
├── apt-packages        # System packages (ffmpeg)
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Local Setup (Testing)

### 1. Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 3. Set Environment Variable

**Linux/Mac:**

```bash
export BOT_TOKEN="your_bot_token_here"
```

**Windows:**

```cmd
set BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Deployment to Render.com (Free Tier)

### Step 1: Prepare Your Repository

1. **Create a GitHub account** (if you don't have one): https://github.com/signup

2. **Create a new repository:**

    - Go to https://github.com/new
    - Name it: `youtube-audio-bot`
    - Make it **Private** (recommended)
    - Don't initialize with README (we already have one)
    - Click "Create repository"

3. **Upload your code to GitHub:**

    ```bash
    # Navigate to your project folder
    cd youtube_audio_bot

    # Initialize git
    git init

    # Add all files
    git add .

    # Commit
    git commit -m "Initial commit"

    # Add your GitHub repository as remote (replace YOUR_USERNAME)
    git remote add origin https://github.com/YOUR_USERNAME/youtube-audio-bot.git

    # Push to GitHub
    git branch -M main
    git push -u origin main
    ```

### Step 2: Deploy to Render.com

1. **Create Render account:**

    - Go to https://render.com
    - Click "Get Started for Free"
    - Sign up with your GitHub account (easiest option)

2. **Create New Web Service:**

    - Click "New +" button in dashboard
    - Select "Web Service"
    - Click "Connect" next to your GitHub account
    - Find and select your `youtube-audio-bot` repository
    - Click "Connect"

3. **Configure the Service:**

    Fill in the following settings:

    - **Name**: `youtube-audio-bot` (or any name you prefer)
    - **Region**: Choose closest to you
    - **Branch**: `main`
    - **Root Directory**: Leave empty
    - **Runtime**: `Python 3`
    - **Build Command**:
        ```
        apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
        ```
    - **Start Command**:
        ```
        python bot.py
        ```
    - **Instance Type**: `Free`

4. **Add Environment Variable:**

    - Scroll down to "Environment Variables"
    - Click "Add Environment Variable"
    - **Key**: `BOT_TOKEN`
    - **Value**: Your Telegram bot token (from BotFather)
    - Click "Add"

5. **Deploy:**
    - Click "Create Web Service" at the bottom
    - Wait 5-10 minutes for deployment
    - Check logs to ensure it says "Bot started successfully!"

### Step 3: Verify Deployment

1. Open Telegram and find your bot
2. Send `/start` command
3. Send a YouTube URL to test
4. You should receive the audio file!

## Important Notes for Render.com Free Tier

⚠️ **Free tier limitations:**

-   Service will spin down after 15 minutes of inactivity
-   First request after spin-down takes 30-60 seconds to wake up
-   750 hours/month free (enough for most personal use)

💡 **To keep it always active:**

-   Upgrade to paid tier ($7/month)
-   Or use a service like UptimeRobot to ping it every 14 minutes

## Usage

Once deployed, your bot is ready to use:

1. Open your bot in Telegram
2. Send `/start` to see welcome message
3. Send `/help` to see instructions
4. Send any YouTube URL to convert

Example:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The bot will:

-   ⏳ Fetch video information
-   ⬇️ Download audio
-   🎵 Convert to MP3
-   📤 Send audio file(s) with metadata

## Troubleshooting

### Bot not responding after deployment

-   Check Render.com logs for errors
-   Verify BOT_TOKEN is set correctly
-   Ensure service is "Running" in Render dashboard

### "Download error" messages

-   Video might be age-restricted
-   Video might be private or deleted
-   Geographic restrictions might apply

### Files not splitting correctly

-   Check that FFmpeg is installed (should be automatic on Render)
-   Verify the video is actually large (>30 minutes at high quality)

### Service keeps spinning down

-   This is normal on free tier
-   First request after inactivity will be slow
-   Consider upgrading to paid tier for 24/7 availability

## Cost Summary

-   **Development**: Free (DIY)
-   **Hosting**:
    -   Free tier: $0/month (with limitations)
    -   Paid tier: $7/month (recommended for 24/7)
-   **Storage**: Included (temporary files only)
-   **Total**: $0-7/month

## Future Enhancements (Optional)

-   Add support for playlists
-   Support other platforms (SoundCloud, etc.)
-   User whitelist/blacklist
-   Usage statistics
-   Custom audio quality selection
-   Download history

## Support

If you encounter issues:

1. Check the logs in Render dashboard
2. Verify your bot token is correct
3. Test with different YouTube videos
4. Ensure FFmpeg is installed

## License

Free to use for personal projects.

---

**Enjoy your YouTube Audio Converter Bot! 🎵**
