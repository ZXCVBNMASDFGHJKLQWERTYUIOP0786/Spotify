import os
import re
import asyncio
import aiohttp
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from youtubesearchpython.future import VideosSearch

# ================= CONFIG =================

# ⚠️ REPLACE WITH YOUR REAL VALUES
API_ID = 123456 
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

PROJECT_ROOT = "TNC_MUSIC"
TEMP_DIR = f"{PROJECT_ROOT}/temp"
ASSETS_DIR = f"{PROJECT_ROOT}/assets"
YOUTUBE_IMG_URL = "https://i.imgur.com/4LwPLai.png"

# Create directories if they don't exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

app = Client(
    "AutoThumbMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= THUMB HELPERS =================

async def download_image(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(path, "wb") as f:
                    await f.write(await resp.read())

def create_rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask

def clean_text(text):
    return re.sub(r"[^\w\s\-\.\,\!\?\'\"]", "", text)

# ================= CUSTOM THUMB =================

async def create_custom_thumbnail(url, title, duration, videoid):
    temp = f"{TEMP_DIR}/thumb_{videoid}.jpg"
    final = f"{TEMP_DIR}/final_{videoid}.jpg"

    await download_image(url, temp)

    try:
        img = Image.open(temp).convert("RGBA")
        canvas = Image.new("RGB", (1280, 720), (0, 0, 0))

        # Background with Blur and Darkening
        bg = img.resize((1280, 720)).filter(ImageFilter.GaussianBlur(22))
        bg = ImageEnhance.Brightness(bg).enhance(0.6)
        canvas.paste(bg, (0, 0))

        # Center Thumbnail with Rounded Corners
        thumb = img.resize((485, 305))
        mask = create_rounded_mask((485, 305), 30)
        canvas.paste(thumb, (397, 110), mask)

        draw = ImageDraw.Draw(canvas)
        font_path = f"{ASSETS_DIR}/font.ttf"

        # Load Font or Fallback
        try:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 38)
                dur_font = ImageFont.truetype(font_path, 24)
            else:
                title_font = dur_font = ImageFont.load_default()
        except:
            title_font = dur_font = ImageFont.load_default()

        # Clean and Truncate Title
        title = clean_text(title)
        if len(title) > 30:
            title = title[:27] + "..."

        # Draw Text
        draw.text((640, 450), title, fill="white", font=title_font, anchor="mm")
        draw.text((640, 510), f"Duration: {duration}", fill="lightgray", font=dur_font, anchor="mm")
        draw.text((1100, 30), "TNC MUSIC", fill="white", font=dur_font)

        canvas.save(final, quality=95)
    except Exception as e:
        print(f"Thumb Gen Error: {e}")
        return temp # Fallback to original image if generation fails
    finally:
        if os.path.exists(temp):
            os.remove(temp)

    return final

# ================= GET THUMB =================

async def get_thumb(videoid):
    try:
        search = VideosSearch(f"https://youtube.com/watch?v={videoid}", limit=1)
        result = (await search.next())["result"][0]

        title = result["title"]
        duration = result.get("duration", "00:00")
        thumb_url = result["thumbnails"][0]["url"].split("?")[0]

        return await create_custom_thumbnail(thumb_url, title, duration, videoid)
    except Exception as e:
        print(f"Get Thumb Error: {e}")
        return YOUTUBE_IMG_URL

# ================= CLEANUP =================

async def cleanup_temp():
    while True:
        await asyncio.sleep(3600)
        try:
            for f in os.listdir(TEMP_DIR):
                path = os.path.join(TEMP_DIR, f)
                if os.path.isfile(path):
                    if (asyncio.get_event_loop().time() - os.path.getmtime(path)) > 3600:
                        os.remove(path)
        except Exception as e:
            print(f"Cleanup Error: {e}")

# ================= PLAY COMMAND =================

@app.on_message(filters.command("play"))
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /play [song name]")

    query = " ".join(message.command[1:])
    msg = await message.reply_text("🔍 Searching...")

    try:
        search = VideosSearch(query, limit=1)
        res = await search.next()
        
        if not res or not res.get("result"):
             return await msg.edit_text("❌ Song not found.")
             
        result = res["result"][0]
        videoid = result["id"]
        title = result["title"]

        # Generate Thumbnail
        thumb = await get_thumb(videoid)

        # FIXED: This block is now indented correctly inside the function
        await msg.edit_media(
            media=InputMediaPhoto(
                media=thumb,
                caption=f"🎧 **Now Playing**\n\n🎵 **Title:** `{title}`\n🆔 **ID:** `{videoid}`"
            )
        )
        
        # Add your Music Player Logic here (PyTgCalls, etc.)
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# ================= START =================

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply_text(
        "🎵 **Auto Thumbnail Music Bot**\n\n"
        "Use `/play song name` to test.\n"
        "Every song gets a generated thumbnail! 🔥"
    )

# ================= RUN =================

if __name__ == "__main__":
    print("Bot Started...")
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_temp())
    app.run()