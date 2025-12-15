import re
import time
import json
import asyncio
import aiohttp

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)
from motor.motor_asyncio import AsyncIOMotorClient


from KanhaMusic import app
from config 


# =========================================================
# CONFIG
# =========================================================

TELEGRAM_API = "https://api.telegram.org"
AI_API_URL = "https://cheak-pearl.vercel.app/api/ai"

CONFIG = {
    "CACHE_TTL": 600,
    "FLOOD_LIMIT": 7,
    "FLOOD_WINDOW": 5,
    "DEFAULT_SETTINGS": {
        "enabled": True,
        "ai_enabled": False,
        "antilink": True,
        "antispam": True,
        "welcome": True,
        "strict_mode": False,
        "max_warnings": 3
    }
}

PATTERNS = {
    "NSFW_KEYWORDS": [
        "porn","sex","nude","xxx","dick","cock","pussy","vagina",
        "bitch","whore","slut","asshole","cum","orgasm",
        "hentai","rape","suicide","behead","nazi","hitler"
    ],
    "RTL": re.compile(r"[\u0600-\u06FF\u200E\u200F\u202A-\u202E]"),
    "URL": re.compile(r"(https?:\/\/|t\.me\/|telegram\.me\/|www\.)", re.I),
    "BAD_STICKERS": {"nsfw","porn","sex","xxx","18+","ahegao"}
}

# =========================================================
# BOT INIT
# =========================================================



mongo = AsyncIOMotorClient("MONGO_DB_URI")
db = mongo.aegisguard

settings_db = db.settings
warn_db = db.warns
flood_db = db.flood
admin_cache = db.admin_cache

# =========================================================
# UTILITIES (EXACT LOGIC)
# =========================================================

def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())

async def get_settings(chat_id):
    data = await settings_db.find_one({"_id": chat_id})
    return {**CONFIG["DEFAULT_SETTINGS"], **(data or {})}

async def save_settings(chat_id, data):
    await settings_db.update_one(
        {"_id": chat_id},
        {"$set": data},
        upsert=True
    )

async def fetch_is_admin(chat_id, user_id):
    try:
        m = await app.get_chat_member(chat_id, user_id)
        return m.status in ("administrator", "creator")
    except:
        return False

async def check_admin_cached(chat_id, user_id):
    key = f"{chat_id}:{user_id}"
    cached = await admin_cache.find_one({"_id": key})

    if cached and time.time() - cached["ts"] < CONFIG["CACHE_TTL"]:
        return cached["admin"]

    is_admin = await fetch_is_admin(chat_id, user_id)
    await admin_cache.update_one(
        {"_id": key},
        {"$set": {"admin": is_admin, "ts": time.time()}},
        upsert=True
    )
    return is_admin

# =========================================================
# FLOOD PROTECTION
# =========================================================

async def check_flood(chat_id, user_id):
    key = f"{chat_id}:{user_id}"
    now = time.time()

    data = await flood_db.find_one({"_id": key})
    if not data or now - data["ts"] > CONFIG["FLOOD_WINDOW"]:
        await flood_db.update_one(
            {"_id": key},
            {"$set": {"count": 1, "ts": now}},
            upsert=True
        )
        return False

    if data["count"] >= CONFIG["FLOOD_LIMIT"]:
        return True

    await flood_db.update_one(
        {"_id": key},
        {"$inc": {"count": 1}}
    )
    return False

# =========================================================
# AI CHECK
# =========================================================

async def check_ai(text):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{AI_API_URL}?prompt=Classify as SAFE or UNSAFE (porn/nsfw): {text}",
                timeout=2
            ) as r:
                res = (await r.text()).upper()
                return "UNSAFE" in res or "PORN" in res
    except:
        return False

# =========================================================
# PUNISHMENT SYSTEM
# =========================================================

async def handle_punishment(chat_id, user, reason, settings):
    key = f"{chat_id}:{user.id}"
    data = await warn_db.find_one({"_id": key})
    count = (data["count"] if data else 0) + 1

    if count >= settings["max_warnings"]:
        if settings["strict_mode"]:
            await app.ban_chat_member(chat_id, user.id)
            text = f"🚫 **Banned** {user.mention}\nReason: Max warnings"
        else:
            await app.restrict_chat_member(
                chat_id,
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 86400
            )
            text = f"🔇 **Muted 24h** {user.mention}"

        await warn_db.delete_one({"_id": key})
    else:
        await warn_db.update_one(
            {"_id": key},
            {"$set": {"count": count}},
            upsert=True
        )
        text = f"⚠️ **Warning {count}/{settings['max_warnings']}**\n{reason}"

    await app.send_message(chat_id, text)

# =========================================================
# PROTECTION ENGINE (BRAIN)
# =========================================================

async def protect_group(msg: Message):
    chat_id = msg.chat.id
    user = msg.from_user
    settings = await get_settings(chat_id)

    if not settings["enabled"]:
        return

    raw_text = msg.text or msg.caption or ""
    clean_text = normalize_text(raw_text)
    violation = None

    if settings["antispam"]:
        if await check_flood(chat_id, user.id):
            await msg.delete()
            await app.restrict_chat_member(
                chat_id,
                user.id,
                ChatPermissions(can_send_messages=False),
                until_date=int(time.time()) + 300
            )
            await app.send_message(chat_id, f"⚡ Anti-Flood muted {user.mention}")
            return

    if settings["antilink"] and PATTERNS["URL"].search(raw_text):
        violation = "Link Detected"

    if not violation:
        for w in PATTERNS["NSFW_KEYWORDS"]:
            if w in clean_text:
                violation = f"Profanity ({w})"
                break

    if not violation and PATTERNS["RTL"].search(raw_text):
        violation = "Forbidden RTL Characters"

    if not violation and settings["ai_enabled"] and len(clean_text) > 8:
        if await check_ai(raw_text):
            violation = "AI Detection"

    if violation:
        await msg.delete()
        await handle_punishment(chat_id, user, violation, settings)

# =========================================================
# COMMANDS
# =========================================================

@app.on_message(filters.private & filters.command(["start", "help"]))
async def start(_, msg):
    await msg.reply_text(
        "🛡️ **AegisGuard Titan**\n\n"
        "Add me to group and promote to admin.\n"
        "Use /settings in group."
    )

@app.on_message(filters.group & filters.command("id"))
async def get_id(_, msg):
    await msg.reply_text(f"🆔 Chat: `{msg.chat.id}`\n👤 You: `{msg.from_user.id}`")

@app.on_message(filters.group & filters.command("settings"))
async def settings_cmd(_, msg):
    if not await check_admin_cached(msg.chat.id, msg.from_user.id):
        return

    s = await get_settings(msg.chat.id)
    kb = [
        [InlineKeyboardButton(f"🛡️ Protection: {s['enabled']}", "t_on")],
        [
            InlineKeyboardButton(f"🔗 Anti-Link: {s['antilink']}", "t_link"),
            InlineKeyboardButton(f"🧠 AI: {s['ai_enabled']}", "t_ai")
        ],
        [
            InlineKeyboardButton(f"⚡ Spam: {s['antispam']}", "t_spam"),
            InlineKeyboardButton(f"🚨 Strict: {s['strict_mode']}", "t_strict")
        ],
        [InlineKeyboardButton("❌ Close", "close")]
    ]

    await msg.reply_text(
        "⚙️ **AegisGuard Config**",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# =========================================================
# CALLBACKS
# =========================================================

@app.on_callback_query()
async def callbacks(_, q: CallbackQuery):
    chat_id = q.message.chat.id

    if not await check_admin_cached(chat_id, q.from_user.id):
        return

    s = await get_settings(chat_id)

    if q.data == "close":
        await q.message.delete()
        return

    if q.data == "t_on": s["enabled"] = not s["enabled"]
    if q.data == "t_link": s["antilink"] = not s["antilink"]
    if q.data == "t_ai": s["ai_enabled"] = not s["ai_enabled"]
    if q.data == "t_spam": s["antispam"] = not s["antispam"]
    if q.data == "t_strict": s["strict_mode"] = not s["strict_mode"]

    await save_settings(chat_id, s)

    await q.answer("Updated ✅")
    await q.message.edit_reply_markup(
        InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🛡️ Protection: {s['enabled']}", "t_on")],
            [InlineKeyboardButton("❌ Close", "close")]
        ])
    )

# =========================================================
# WATCHER
# =========================================================

@app.on_message(filters.group & ~filters.service)
async def watcher(_, msg: Message):
    if await check_admin_cached(msg.chat.id, msg.from_user.id):
        return
    await protect_group(msg)

