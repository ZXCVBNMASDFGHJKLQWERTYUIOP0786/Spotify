#
# Copyright (C) 2025-2026 by OyeKanhaa@Github
#
# This file is part of < https://github.com/OyeKanhaa/KanhaMusic >
# Released under GNU v3.0 License Agreement
#

from pyrogram.types import InlineKeyboardButton

import config
from KanhaMusic import app


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
            )
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
                callback_data="settings_back_helper",
            )
        ],
    ]
    return buttons