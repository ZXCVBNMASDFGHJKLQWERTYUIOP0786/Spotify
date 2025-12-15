import re
import time
import asyncio
import aiohttp
from urllib.parse import quote

from pyrogram import filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)

from motor.motor_asyncio import AsyncIOMotorClient

from KanhaMusic import app
from config import MONGO_DB_URI

# =========================================================
# CONFIG
# =========================================================

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
}

# =========================================================
# DATABASE
# =========================================================

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo.aegisguard

settings_db = db.settings
warn_db = db.warns
flood_db = db.flood
admin_cache = db.admin_cache

# =========================================================
# HELPERS
# =========================================================

def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())

async def get_settings(chat_id: int):
    data = await settings_db.find_one({"_id": chat_id})
    return {**CONFIG["DEFAULT_SETTINGS"], **(data or {})}

async def save_settings(chat_id: int, data: dict):
    await settings_db.update_one(
        {"_id": chat_id},
        {"$set": data},
        upsert=True
    )

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

async def check_admin_cached(chat_id: int, user_id: int) -> bool:
    key = f"{chat_id}:{user_id}"
    now = time.time()

    data = await admin_cache.find_one({"_id": key})
    if data and now - data["ts"] < CONFIG["CACHE_TTL"]:
        return data["admin"]

    admin = await is_admin(chat_id, user_id)
    await admin_cache.update_one(
        {"_id": key},
        {"$set": {"admin": admin, "ts": now}},
        upsert=True
    )
    return admin

# =========================================================
# FLOOD
# =========================================================

async def check_flood(chat_id: int, user_id: int) -> bool:
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

async def check_ai(text: str) -> bool:
    try:
        prompt = quote(f"Classify as SAFE or UNSAFE (porn/nsfw): {text}")
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{AI_API_URL}?prompt={prompt}", timeout=3) as r:
                res = (await r.text()).upper()
                return "UNSAFE" in res or "PORN" in res
    except:
        return False

# =========================================================
# PUNISHMENT
# =========================================================

async def punish(chat_id: int, user, reason: str, settings: dict):
    key = f"{chat_id}:{user.id}"
    data = await warn_db.find_one({"_id": key})
    count = (data["count"] if data else 0) + 1

    if count >= settings["max_warnings"]:
        if settings["strict_mode"]:
            await app.ban_chat_member(chat_id, user.id)
            text = f"🚫 **Banned** {user.mention}\nReason: {reason}"
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
# PROTECTION
# =========================================================

async def protect(msg: Message):
    if not msg.from_user:
        return

    chat_id = msg.chat.id
    user = msg.from_user
    settings = await get_settings(chat_id)

    if not settings["enabled"]:
        return

    text = msg.text or msg.caption or ""
    clean = normalize_text(text)
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
            return

    if settings["antilink"] and PATTERNS["URL"].search(text):
        violation = "Link detected"

    if not violation:
        for w in PATTERNS["NSFW_KEYWORDS"]:
            if w in clean:
                violation = f"NSFW word: {w}"
                break

    if not violation and PATTERNS["RTL"].search(text):
        violation = "RTL characters"

    if not violation and settings["ai_enabled"] and len(clean) > 8:
        if await check_ai(text):
            violation = "AI unsafe text"

    if violation:
        await msg.delete()
        await punish(chat_id, user, violation, settings)

# =========================================================
# COMMANDS
# =========================================================



@app.on_message(filters.group & filters.command("gpset"))
async def settings_cmd(_, msg):
    if not await check_admin_cached(msg.chat.id, msg.from_user.id):
        return

    s = await get_settings(msg.chat.id)
    await msg.reply_text(
        "⚙️ **AegisGuard Settings**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🛡️ Protection: {s['enabled']}", "t_on")],
            [InlineKeyboardButton(f"🔗 Anti-Link: {s['antilink']}", "t_link")],
            [InlineKeyboardButton(f"🧠 AI: {s['ai_enabled']}", "t_ai")],
            [InlineKeyboardButton(f"⚡ Spam: {s['antispam']}", "t_spam")],
            [InlineKeyboardButton(f"🚨 Strict: {s['strict_mode']}", "t_strict")],
            [InlineKeyboardButton("❌ Close", "close")]
        ])
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
        return await q.message.delete()

    if q.data == "t_on": s["enabled"] = not s["enabled"]
    if q.data == "t_link": s["antilink"] = not s["antilink"]
    if q.data == "t_ai": s["ai_enabled"] = not s["ai_enabled"]
    if q.data == "t_spam": s["antispam"] = not s["antispam"]
    if q.data == "t_strict": s["strict_mode"] = not s["strict_mode"]

    await save_settings(chat_id, s)
    await q.answer("Updated ✅")
    await q.message.edit_text("⚙️ **Settings Updated**", reply_markup=q.message.reply_markup)

# =========================================================
# WATCHER
# =========================================================

@app.on_message(filters.group & ~filters.service)
async def watcher(_, msg: Message):
    if not msg.from_user:
        return

    if await check_admin_cached(msg.chat.id, msg.from_user.id):
        return

    await protect(msg)