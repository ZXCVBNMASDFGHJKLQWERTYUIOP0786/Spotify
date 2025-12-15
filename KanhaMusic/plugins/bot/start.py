import time
import asyncio
import random

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from KanhaMusic import app
from KanhaMusic.plugins.sudo.sudoers import sudoers_list
from KanhaMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
)
from KanhaMusic.utils.decorators.language import LanguageStart
from KanhaMusic.utils.formatters import get_readable_time
from KanhaMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


# ============================
#        BOT BOOT TIME
# ============================
_boot_ = time.time()


NEXIO = [
    "https://files.catbox.moe/wy1exf.jpg",
    "https://files.catbox.moe/hdo3d0.jpg",
    "https://files.catbox.moe/pf0ouq.jpg",
    "https://files.catbox.moe/hsmyvi.jpg",
    "https://files.catbox.moe/whnfs1.jpg",
]

# Effect IDs
EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

emojis = ["🥰", "🔥", "💖", "😁", "😎", "🌚", "❤️‍🔥", "♥️", "🎉", "🙈"]


# ============================
#        START — PRIVATE
# ============================

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):

    # SAVE USER
    await add_served_user(message.from_user.id)

    # Reaction
    try:
        await message.react(random.choice(emojis))
    except:
        pass

    # ---- START WITH PARAMETER ----
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            return await message.reply_photo(
                random.choice(NEXIO),
                has_spoiler=True,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=help_pannel(_),
            )

        if name.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "")
            query_url = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query_url, limit=1)
            search_result = await results.next()

            if not search_result["result"]:
                await m.edit("❌ No results found.")
                return

            result = search_result["result"][0]
            title = result["title"]
            duration = result["duration"]
            views = result.get("viewCount", {}).get("short", "N/A")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channellink = result["channel"]["link"]
            channel = result["channel"]["name"]
            link = result["link"]
            published = result.get("publishedTime", "N/A")

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )

            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                    ]
                ]
            )

            await m.delete()
            return await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                has_spoiler=True,
                caption=searched_text,
                reply_markup=key,
            )

    # ============================
    #  START NORMAL (NO PARAMETER)
    # ============================
    
    # Direct Photo Send (Text animation removed)
    await message.reply_photo(
        photo=random.choice(NEXIO),
        caption=_["start_2"].format(
            message.from_user.mention,
            app.mention
        ),
        has_spoiler=True,
        reply_markup=InlineKeyboardMarkup(private_panel(_))
    )


# ============================
#        START — GROUP
# ============================

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):

    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        random.choice(NEXIO),
        has_spoiler=True,
        caption=_["start_1"].format(
            app.mention,
            get_readable_time(uptime),
        ),
        reply_markup=InlineKeyboardMarkup(
            start_panel(_)
        ),
    )

    await add_served_chat(message.chat.id)


# ============================
#          WELCOME
# ============================

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):

    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # Ban check
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            # If Bot is added
            if member.id == app.id:

                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                await message.reply_photo(
                    random.choice(NEXIO),
                    has_spoiler=True,
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        start_panel(_)
                    ),
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as e:
            print(e)
