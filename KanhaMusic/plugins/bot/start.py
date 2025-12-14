import time, asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
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

    # Sticker animation
    sticker = await message.reply_sticker(random.choice(PURVI_STKR))
    await asyncio.sleep(1)
    await sticker.delete()

    # ---- START WITH PARAMETER ----
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            return await message.reply_photo(
                random.choice(NEXIO),
                has_spoiler=True,
                message_effect_id=random.choice(EFFECT_IDS),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=help_pannel(_),
            )

        if name.startswith("sud"):
            return await sudoers_list(client=client, message=message, _=_)

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "")
            query = f"https://www.youtube.com/watch?v={query}"

            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

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
                message_effect_id=random.choice(EFFECT_IDS),
                reply_markup=key,
            )

    # ============================
    #      NORMAL START (FIXED)
    # ============================

    rishu = await message.reply_photo(
        photo=random.choice(NEXIO),
        has_spoiler=True,
        message_effect_id=random.choice(EFFECT_IDS),
        caption=f"<b>ʜᴇʏ ʙᴧʙʏ {message.from_user.mention}</b>",
    )

    await asyncio.sleep(0.4)

    await rishu.edit_caption(
        "<b>ɪ ᴧᴍ ʏᴏᴜʀ ᴍᴜsɪᴄ ʙᴏᴛ..🦋</b>"
    )

    await asyncio.sleep(0.4)

    await rishu.edit_caption(
        _["start_2"].format(
            message.from_user.mention,
            app.mention
        ),
        reply_markup=InlineKeyboardMarkup(
            private_panel(_)
        ),
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

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

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