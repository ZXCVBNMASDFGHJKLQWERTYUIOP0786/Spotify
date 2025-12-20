import re
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

# ===== CLIENT (NO API / TOKEN HERE) =====
app = Client("BioLinkGuardBot")

# ===== MEMORY =====
BIO_LINK = {}
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

# ===== COMMAND: /biolink =====
@app.on_message(filters.command("biolink") & filters.group)
async def biolink_toggle(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply("ℹ️ Usage: /biolink on | /biolink off")

    BIO_LINK[message.chat.id] = message.command[1].lower() == "on"
    await message.reply("✅ Bio Link Guard updated successfully.")

# ===== COMMAND: /setlog =====
@app.on_message(filters.command("setlog") & filters.group)
async def set_log(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    try:
        LOG_CHANNEL[message.chat.id] = int(message.command[1])
        await message.reply("📢 Log channel set successfully.")
    except:
        await message.reply("❌ Invalid channel ID.")

# ===== WATCHER =====
@app.on_message(filters.group & filters.text)
async def bio_checker(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not BIO_LINK.get(chat_id):
        return

    # Admin / Owner safe
    if await is_admin(client, chat_id, user_id):
        return

    # Cooldown (10 sec)
    now = time.time()
    if COOLDOWN.get(user_id, 0) > now:
        return
    COOLDOWN[user_id] = now + 10

    try:
        user = await client.get_users(user_id)
    except:
        return

    bio = user.bio or ""
    if not LINK_REGEX.search(bio):
        return

    # Delete message
    try:
        await message.delete()
    except:
        return

    # 🔄 Progress bar animation
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
        await asyncio.sleep(0.25)
        try:
            await anim.edit(f"🔎 Checking profile...\n\n{bar}")
        except:
            pass

    # ⚠️ FINAL WARNING (BOLD + EMOJI)
    await anim.edit(
        f"⚠️ WARNING ALERT ⚠️\n\n"
        f"👤 {message.from_user.mention}\n\n"
        "🔗 Your profile bio contains a link.\n"
        "🚫 Links are not allowed in this group.\n\n"
        "📝 Please remove the link from your bio\n"
        "✅ and try sending your message again."
    )

    # Auto delete warning
    await asyncio.sleep(10)
    try:
        await anim.delete()
    except:
        pass

    # Log channel (optional)
    log_id = LOG_CHANNEL.get(chat_id)
    if log_id:
        await client.send_message(
            log_id,
            f"🔗 Bio Link Blocked\n\n"
            f"👤 User: {message.from_user.mention}\n"
            f"🆔 ID: {user_id}\n"
            f"📝 Bio:\n{bio}"
        )

# ===== START =====
app.run()