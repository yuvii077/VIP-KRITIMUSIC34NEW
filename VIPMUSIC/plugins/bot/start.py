#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
#
import asyncio
import time
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_string
from VIPMUSIC import HELPABLE, Telegram, YouTube, app
from VIPMUSIC.misc import SUDOERS, _boot_
from VIPMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_assistant,
    get_lang,
    get_userss,
    is_banned_user,
    is_on_off,
    is_served_private_chat,
)
from VIPMUSIC.utils.decorators.language import LanguageStart
from VIPMUSIC.utils.formatters import get_readable_time
from VIPMUSIC.utils.functions import MARKDOWN, WELCOMEHELP

# FIXING IMPORT ERROR: Try common spellings used in VIP-MUSIC repos
try:
    from VIPMUSIC.utils.inline import alive_panel, private_panel, start_pannel
except ImportError:
    from VIPMUSIC.utils.inline import alive_pannel as alive_panel, private_panel, start_pannel

from .help import paginate_modules

loop = asyncio.get_running_loop()

def get_log_id():
    log_id = config.LOG_GROUP_ID
    if not log_id: return None
    try:
        log_id = str(log_id).strip()
        if not log_id.startswith("-100"):
            return int(f"-100{log_id}") if not log_id.startswith("-") else int(log_id)
        return int(log_id)
    except: return log_id

@app.on_message(group=-1)
async def ban_new(client, message):
    if not message.from_user: return
    if await is_banned_user(message.from_user.id):
        try:
            await message.chat.ban_member(message.from_user.id)
            await message.reply_text("<b>⚠️ Access Denied:</b> You are banned from using this bot.")
        except: pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    try: await message.react("⚡")
    except: pass
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", close=True))
            return await message.reply_photo(photo=START_IMG_URL, caption=_["help_1"], reply_markup=keyboard)
        
        if name[0:4] == "song":
            return await message.reply_text(_["song_2"])

        if name == "mkdwn_help":
            return await message.reply(MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        if name[0:3] == "sta":
            m = await message.reply_text("<b>🔍 Fetching Premium Stats...</b>")
            stats = await get_userss(message.from_user.id)
            if not stats: return await m.edit(_["ustats_1"])

            def get_stats():
                results = {str(i): stats[i]["spot"] for i in stats}
                list_arranged = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                msg, limit, tota, videoid = "", 0, 0, None
                for vidid, count in list_arranged.items():
                    tota += count
                    if limit == 10: continue
                    if limit == 0: videoid = vidid
                    limit += 1
                    title = (stats.get(vidid)["title"][:30]).title()
                    msg += f"<b>{limit}»</b> <code>{title}</code>\n<b>└ Played:</b> <code>{count} times</code>\n\n"
                return videoid, _["ustats_2"].format(len(stats), tota, limit) + msg

            try:
                videoid, msg = await loop.run_in_executor(None, get_stats)
                thumbnail = await YouTube.thumbnail(videoid, True)
                await m.delete()
                await message.reply_photo(photo=thumbnail, caption=msg)
            except: await m.edit("<b>❌ Error fetching stats.</b>")
            return

    # MAIN START MESSAGE (PREMIUM LOOK)
    out = private_panel(_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
        message_effect_id="5311823902341673323" 
    )

    if await is_on_off(config.LOG):
        try:
            await app.send_message(get_log_id(), f"<b>#NewUser</b>\n\n<b>👤 User:</b> {message.from_user.mention}\n<b>🆔 ID:</b> <code>{message.from_user.id}</code>")
        except: pass

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def testbot(client, message: Message, _):
    out = alive_panel(_)
    uptime = get_readable_time(int(time.time() - _boot_))
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_7"].format(app.mention, uptime),
        reply_markup=InlineKeyboardMarkup(out),
    )
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True) and not await is_served_private_chat(chat_id):
        await message.reply_text("<b>🔒 Private Mode Active:</b> Leaving group.")
        return await app.leave_chat(chat_id)
    
    await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(chat_id)
            _ = get_string(language)
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_5"])
                    return await app.leave_chat(chat_id)
                userbot = await get_assistant(chat_id)
                await message.reply_text(_["start_2"].format(app.mention, userbot.username, userbot.id), reply_markup=InlineKeyboardMarkup(start_pannel(_)))
            
            if member.id in config.OWNER_ID:
                await message.reply_text(f"<b>👑 Owner {member.mention} has joined the chat!</b>")
            elif member.id in SUDOERS:
                await message.reply_text(f"<b>🛡️ Sudo User {member.mention} has joined!</b>")
        except: pass

__MODULE__ = "Bᴏᴛ"
__HELP__ = """
<b>✨ <u>Pʀᴇᴍɪᴜᴍ Mᴜsɪᴄ Cᴏᴍᴍᴀɴᴅs</u> ✨</b>

<b>🎵 Pʟᴀʏᴇʀ Fᴜɴᴄᴛɪᴏɴs:</b>
<b>• /play</b> <code>[Song Name/URL]</code> - Play music in VC
<b>• /stats</b> - Get top 10 played songs
<b>• /lyrics</b> - Search song lyrics
<b>• /song</b> - Download high quality MP3

<b>🛡️ Sᴜᴅᴏ Fᴜɴᴄᴛɪᴏɴs:</b>
<b>• /sudolist</b> - Check authorized users
<b>• /reboot</b> - Refresh the bot system

<b>🌟 <u>Eɴᴊᴏʏ Sᴇᴀᴍʟᴇss Mᴜsɪᴄ</u> 🌟
