#
# Copyright (C) 2025-2026 by OyeKanhaa@Github, < https://github.com/OyeKanhaa >.
#
# This file is part of < https://github.com/OyeKanhaa/KanhaMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/OyeKanhaa/KanhaMusic/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.types import InlineKeyboardButton

import config
from KanhaMusic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
        [
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons
