#
# Copyright (C) 2025-2026 by OyeKanhaa@Github
#
# This file is part of < https://github.com/OyeKanhaa/KanhaMusic >
# Released under GNU v3.0 License Agreement
#

import sys
import platform
from time import time
from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup

import config
from KanhaMusic import app

# ──────────────────────────────
# GLOBAL VARIABLES
# ──────────────────────────────
# Bot start time (uptime ke liye)
BOT_START_TIME = datetime.now()

# ──────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────

def get_uptime():
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# ──────────────────────────────
# START / HOME PANEL
# ──────────────────────────────
def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],  # ✙ Add Me ✙
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"],  # Support
                callback_data="support_menu",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],  # Help & Commands
                callback_data="settings_back_helper",
            ),
        ],
    ]
    return buttons


# ──────────────────────────────
# PRIVATE PANEL
# ──────────────────────────────
def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],  # Add me in your group
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_9"],  # Support
                callback_data="support_menu",
            ),
            # FIX: Yahan comma aur closing bracket missing tha
            InlineKeyboardButton(
                text="📨ʏᴛ-ᴀᴘɪ", 
                callback_data="oapi"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],  # Help & Commands
                callback_data="settings_back_helper",
            )
        ],
    ]
    return buttons


# ──────────────────────────────
# SUPPORT SUB MENU
# ──────────────────────────────
def support_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="👑 OWNER",
                user_id=config.OWNER_ID,
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 SUPPORT",
                url=config.SUPPORT_CHAT,
            ),
            InlineKeyboardButton(
                text="📢 UPDATES",
                url=config.SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 BACK",
                callback_data="settings_back_helper", # Fixed callback to match Home/Back logic
            )
        ],
    ]
    return buttons


# ──────────────────────────────
# API STATUS CALLBACK HANDLER
# ──────────────────────────────

@app.on_callback_query(filters.regex("oapi"))
async def show_bot_info(c: Client, q: CallbackQuery):
    start = time()
    try:
        # Ping calculate karne ke liye dummy message bhej rahe hain
        m = await c.send_message(q.message.chat.id, "🧾 ᴄʜᴇᴄᴋɪɴɢ ᴀᴘɪ sᴛᴀᴛᴜs...")
        delta_ping = (time() - start) * 1000
        await m.delete()
        
        # Short popup text
        short_txt = f"""
🧾 <b>ᴀᴘɪ sᴛᴀᴛᴜs</b>

<b>ᴅʙ :</b> 🟢 ᴏɴʟɪɴᴇ
<b>ʀɪsʜᴜ ᴀᴘɪ :</b> 🟢 ʀᴇsᴘᴏɴsɪᴠᴇ
<b>ᴀᴘɪ ᴘɪɴɢ :</b> <code>{delta_ping:.2f} ms</code>
<b>ᴀᴘɪ ᴜᴘᴛɪᴍᴇ :</b> <code>{get_uptime()}</code>

✅ ᴇᴠᴇʀʏᴛʜɪɴɢ ғɪɴᴇ
"""
        await q.answer(short_txt.strip(), show_alert=True)
    except Exception as e:
        await q.answer(f"Error: {str(e)}", show_alert=True)
