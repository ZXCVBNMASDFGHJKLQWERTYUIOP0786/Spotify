from pyrogram import filters
from pyrogram.types import Message
from KanhaMusic import app
import asyncio
import random

# ================= COMMON FUNCTION =================

async def run_prank(message, title, target, steps, end_msgs):
    msg = await message.reply_text(
        f"{title}\n\n🎯 Target: {target}",
        quote=True
    )
    await asyncio.sleep(1.5)

    for step in steps:
        await msg.edit(f"{title}\n\n🎯 Target: {target}\n\n{step}")
        await asyncio.sleep(random.uniform(1.2, 2.0))

    await asyncio.sleep(1.5)
    await msg.edit(
        f"🚨 PROCESS COMPLETE 🚨\n\n"
        f"🎯 Target: {target}\n\n"
        f"{random.choice(end_msgs)}"
    )

# ================= HACK =================

@app.on_message(filters.command("hack"))
async def hack(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /hack username")
    await run_prank(
        message,
        "😈 HACKING STARTED 😈",
        " ".join(message.command[1:]),
        [
            "🔐 Password crack ho raha hai...",
            "💻 Firewall bypass...",
            "📂 Files access mil gaya...",
        ],
        ["🤣 PRANK THA!", "😂 Kuch bhi hack nahi hua"]
    )

# ================= MOBILE =================

@app.on_message(filters.command("mobile"))
async def mobile(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /mobile username")
    await run_prank(
        message,
        "📱 MOBILE DATA EXTRACT 📱",
        " ".join(message.command[1:]),
        [
            "📡 IMEI trace...",
            "🗺 Location ping...",
            "📂 Gallery copy...",
        ],
        ["😜 Mobile safe hai", "🤣 PRANK"]
    )

# ================= BAN =================

@app.on_message(filters.command("banprank"))
async def ban(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /banprank username")
    await run_prank(
        message,
        "⛔ TELEGRAM BAN CHECK ⛔",
        " ".join(message.command[1:]),
        [
            "⚠️ Reports found...",
            "🚫 Violation confirmed...",
        ],
        ["😂 Account safe hai", "🤡 PRANK"]
    )

# ================= VIRUS =================

@app.on_message(filters.command("virus"))
async def virus(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /virus username")
    await run_prank(
        message,
        "🦠 VIRUS SCAN 🦠",
        " ".join(message.command[1:]),
        [
            "🧬 Malware detect...",
            "⚠️ High risk virus found...",
        ],
        ["🤣 Virus kuch nahi", "😜 PRANK"]
    )

# ================= LOCATION =================

@app.on_message(filters.command("location"))
async def location(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /location username")
    await run_prank(
        message,
        "📍 LIVE LOCATION TRACE 📍",
        " ".join(message.command[1:]),
        [
            "🛰 GPS connect...",
            "📡 Signal locked...",
        ],
        ["😂 Location fake thi", "🤡 PRANK"]
    )

# ================= CAMERA =================

@app.on_message(filters.command("camera"))
async def camera(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /camera username")
    await run_prank(
        message,
        "📸 CAMERA ACCESS 📸",
        " ".join(message.command[1:]),
        [
            "📷 Front camera ON...",
            "🎥 Recording started...",
        ],
        ["🤣 Camera kuch nahi", "😜 PRANK"]
    )

# ================= SIM =================

@app.on_message(filters.command("sim"))
async def sim(_, message: Message):

if len(message.command) < 2:
        return await message.reply_text("Usage: /sim username")
    await run_prank(
        message,
        "📵 SIM BLOCK PROCESS 📵",
        " ".join(message.command[1:]),
        [
            "📞 Network disconnect...",
            "❌ SIM suspend...",
        ],
        ["😂 SIM safe hai", "🤡 PRANK"]
    )

# ================= POLICE =================

@app.on_message(filters.command("police"))
async def police(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /police username")
    await run_prank(
        message,
        "🚓 CYBER CRIME NOTICE 🚓",
        " ".join(message.command[1:]),
        [
            "📄 Case registered...",
            "⚖️ Legal action...",
        ],
        ["🤣 Police nahi aayegi", "😜 PRANK"]
    )

# ================= UPDATE =================

@app.on_message(filters.command("update"))
async def update(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /update username")
    await run_prank(
        message,
        "🔔 TELEGRAM UPDATE 🔔",
        " ".join(message.command[1:]),
        [
            "⬇️ Update downloading...",
            "⚠️ Account risk...",
        ],
        ["😂 Fake update", "🤡 PRANK"]
    )

# ================= PAYMENT =================

@app.on_message(filters.command("payment"))
async def payment(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /payment username")
    await run_prank(
        message,
        "💸 PAYMENT ALERT 💸",
        " ".join(message.command[1:]),
        [
            "💳 Transaction processing...",
            "✅ Amount credited...",
        ],
        ["🤣 Paisa nahi aaya", "😜 PRANK"]
    )