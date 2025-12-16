from pyrogram import filters
from pyrogram.types import Message
from KanhaMusic import app
import asyncio
import random

HACK_STEPS = [
    "🔍 Target locate kar raha hoon...",
    "📡 Server se connect ho raha hoon...",
    "🔐 Password brute-force start...",
    "💻 Firewall bypass ho raha hai...",
    "📂 Private files access ho rahi hain...",
    "📸 Camera access mil gaya...",
    "📱 WhatsApp data clone ho raha hai...",
    "💬 Telegram chats decrypt ho rahi hain...",
    "🧠 AI se data analyze ho raha hai...",
    "⚠️ Security alert bypassed...",
]

FINAL_PRANK = [
    "🤣 APRIL FOOL!",
    "🤡 YE SIRF PRANK THA!",
    "😜 Kuch bhi hack nahi hua",
    "😂 System safe hai bhai",
]

@app.on_message(filters.command("hack"))
async def hack_prank(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage: /hack username",
            quote=True
        )

    target = " ".join(message.command[1:])

    msg = await message.reply_text(
        f"😈 HACKING STARTED 😈\n\n🎯 Target: {target}",
        quote=True
    )

    await asyncio.sleep(1.5)

    for step in HACK_STEPS:
        await msg.edit(f"😈 HACKING {target} 😈\n\n{step}")
        await asyncio.sleep(random.uniform(1.2, 2.0))

    await asyncio.sleep(1.5)

    await msg.edit(
        f"🚨 HACK COMPLETE 🚨\n\n"
        f"🎯 Target: {target}\n"
        f"📂 Data: 100% Extracted\n"
        f"🔓 Access: ROOT\n\n"
        f"{random.choice(FINAL_PRANK)}"
    )