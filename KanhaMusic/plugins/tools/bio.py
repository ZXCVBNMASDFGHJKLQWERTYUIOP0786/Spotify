import re
import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from KanhaMusic import app

# ================= STORAGE =================
BIO_LINK = {}
LOG_CHANNEL = {}
COOLDOWN = {}

# ================= LINK REGEX =================
LINK_REGEX = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|bit\.ly|tinyurl)",
    re.I
)

# ================= ADMIN CHECK =================
async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

# ================= /biolink =================
@app.on_message(filters.command("biolink") & filters.group)
async def biolink_toggle(_, message: Message):
    if not await is_admin(app, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")

    if len(message.command) < 2:
        return await message.reply(
            f"BioLink Guard is {'ON' if BIO_LINK.get(message.chat.id) else 'OFF'}\n\n"
            "Use:\n/biolink on\n/biolink off"
        )

    if message.command[1].lower() == "on":
        BIO_LINK[message.chat.id] = True
        await message.reply("✅ BioLink Guard ENABLED")
    elif message.command[1].lower() == "off":
        BIO_LINK[message.chat.id] = False
        await message.reply("❌ BioLink Guard DISABLED")

# ================= WATCHER (FIXED) =================
@app.on_message(filters.group & filters.incoming)
async def bio_checker(_, message: Message):

    # Bot must see message
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Feature OFF
    if not BIO_LINK.get(chat_id):
        return

    # Admin safe
    if await is_admin(app, chat_id, user_id):
        return

    # Cooldown
    now = time.time()
    if COOLDOWN.get((chat_id, user_id), 0) > now:
        return
    COOLDOWN[(chat_id, user_id)] = now + 8

    # Fetch user
    try:
        user = await app.get_users(user_id)
    except:
        return

    bio = getattr(user, "bio", "") or ""

    # No link
    if not LINK_REGEX.search(bio):
        return

    # Delete message
    try:
        await message.delete()
    except:
        pass

    # Warning
    warn = await message.reply(
        f"⚠️ WARNING\n\n"
        f"👤 {message.from_user.mention}\n\n"
        "🔗 Your bio contains a link.\n"
        "🚫 Remove it to chat here."
    )

    await asyncio.sleep(8)
    try:
        await warn.delete()
    except:
        pass