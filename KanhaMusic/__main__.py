#
# Copyright (C) 2021-2022 by OyeKanhaa@Github, < https://github.com/OyeKanhaa >.
# This file is part of < https://github.com/OyeKanhaa/KanhaMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/OyeKanhaa/KanhaMusic/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from KanhaMusic import LOGGER, app, userbot
from KanhaMusic.core.call import Kanha
from KanhaMusic.misc import sudo
from KanhaMusic.plugins import ALL_MODULES
from KanhaMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("KanhaMusic.plugins" + all_module)
    LOGGER("KanhaMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Kanha.start()
    try:
        await Kanha.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("KanhaMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Kanha.decorators()
    LOGGER("KanhaMusic").info(
        "ʙᴏᴛ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ, ɴᴏᴡ ɢɪʙ ʏᴏᴜʀ ɢɪʀʟғʀɪᴇɴᴅ ᴄʜᴜᴛ ɪɴ "
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("KanhaMusic").info("Stopping@kanhasworld")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
