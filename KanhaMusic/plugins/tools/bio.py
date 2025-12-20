import re
import asyncio
import time
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from KanhaMusic import app

# ===== MEMORY =====
BIO_LINK = {}          # <-- ON/OFF store
LOG_CHANNEL = {}
COOLDOWN = {}

# ===== LINK REGEX =====
LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly|tinyurl)",
    re.IGNORECASE
)

# ===== ADMIN CHECK =====
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

# ===== BIOLINK ON/OFF COMMAND =====
@app.on_message(filters.command("biolink") & filters.group)
async def biolink_toggle(_, message: Message):
    if not await is_admin(app, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")

    if len(message.command) < 2:
        status = BIO_LINK.get(message.chat.id, False)
        return await message.reply(
            f"ℹ️ Bio Link Guard is currently {'ON' if status else 'OFF'}\n\n"
            "Usage:\n"
            "/biolink on – Enable\n"
            "/biolink off – Disable"
        )

    arg = message.command[1].lower()

    if arg == "on":
        BIO_LINK[message.chat.id] = True
        await message.reply("✅ Bio Link Guard ENABLED")
    elif arg == "off":
        BIO_LINK[message.chat.id] = False
        await message.reply("❌ Bio Link Guard DISABLED")
    else:
        await message.reply("Usage: /biolink on | /biolink off")

# ===== OPTIONAL: SET LOG CHANNEL =====
@app.on_message(filters.command("setlog") & filters.group)
async def set_log(_, message: Message):
    if not await is_admin(app, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("Usage: /setlog <channel_id>")

    try:
        LOG_CHANNEL[message.chat.id] = int(message.command[1])
        await message.reply("📢 Log channel set successfully.")
    except:
        await message.reply("❌ Invalid channel ID.")

# ===== WATCHER (GROUP ONLY) =====
@app.on_message(filters.group & filters.text)
async def bio_checker(_, message: Message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # 🔘 Check if feature is ON
    if not BIO_LINK.get(chat_id, False):
        return

    # Admin safe
    if await is_admin(app, chat_id, user_id):
        return

    # Cooldown (10 sec per user)
    now = time.time()
    if COOLDOWN.get((chat_id, user_id), 0) > now:
        return
    COOLDOWN[(chat_id, user_id)] = now + 10

    try:
        user = await app.get_users(user_id)
    except:
        return

    bio = getattr(user, "bio", "") or ""

    if not LINK_REGEX.search(bio):
        return

    # Delete message
    try:
        await message.delete()
    except:
        pass

    # 🔄 Progress animation
    anim = await message.reply("🔎 Checking profile...\n\n□□□□□□□□□□")

    bars = [
        "■□□□□□□□□□",
        "■■□□□□□□□□",
        "■■■□□□□□□□",
        "■■■■□□□□□□",
        "■■■■■□□□□□",
        "■■■■■■□□□□",
        "■■■■■■■□□□",
        "■■■■■■■■□□",
        "■■■■■■■■■□",
        "■■■■■■■■■■"
    ]

    for bar in bars:
        await asyncio.sleep(0.2)
        try:
            await anim.edit(f"🔎 Checking profile...\n\n{bar}")
        except:
            pass

    # ⚠️ FINAL WARNING
    await anim.edit(
        f"⚠️ WARNING ALERT ⚠️\n\n"
        f"👤 {message.from_user.mention}\n\n"
        "🔗 Your profile bio contains a link.\n"
        "🚫 Links are not allowed in this group.\n\n"
        "📝 Please remove the link from your bio\n"
        "✅ and try again."
    )

    # Auto delete warning
    await asyncio.sleep(10)
    try:
        await anim.delete()
    except:
        pass

# Log channel
    log_id = LOG_CHANNEL.get(chat_id)
    if log_id:
        await app.send_message(
            log_id,
            f"🔗 Bio Link Blocked\n\n"
            f"👤 User: {message.from_user.mention}\n"
            f"🆔 ID: {user_id}\n"
            f"📝 Bio:\n{bio}"
        )