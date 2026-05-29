#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the MIT License.
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
# ✦ Redesigned with 2026 Futuristic Look ✦
#

import math

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from VIPMUSIC import app
from VIPMUSIC.utils.formatters import time_to_seconds


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🔮 PROGRESS BAR HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_progress_bar(played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    bars = [
        (10,  "█▱▱▱▱▱▱▱▱▱"),
        (20,  "██▱▱▱▱▱▱▱▱"),
        (30,  "███▱▱▱▱▱▱▱"),
        (40,  "████▱▱▱▱▱▱"),
        (50,  "█████▱▱▱▱▱"),
        (60,  "██████▱▱▱▱"),
        (70,  "███████▱▱▱"),
        (80,  "████████▱▱"),
        (90,  "█████████▱"),
        (101, "██████████"),
    ]
    for threshold, bar in bars:
        if umm < threshold:
            return bar
    return "██████████"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎵 STREAM MARKUP (Simple)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def stream_markupp(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"✚ {_['P_B_7']}",
                callback_data=f"add_playlist {videoid}"
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#       ⏱ STREAM MARKUP WITH TIMER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def stream_markup_timerr(_, videoid, chat_id, played, dur):
    bar = get_progress_bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🕐 {played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✚ {_['P_B_7']}",
                callback_data=f"add_playlist {videoid}"
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#       📡 TELEGRAM MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def telegram_markupp(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


def telegram_markup_timer(_, chat_id, played, dur):
    bar = get_progress_bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🕐 {played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


def telegram_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="⚡ ɴᴇxᴛ ⚡", callback_data=f"PanelMarkup None|{chat_id}"),
            InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close"),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#        🔍 SEARCH / TRACK MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def track_markupp(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]
    return buttons


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="⏹ ᴇɴᴅ", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⚙️ ᴍᴏʀᴇ",
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
    ]
    return buttons


def playlist_markupp(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {videoid}|{user_id}"
            ),
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"VIPPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🔴 LIVE STREAM MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def livestream_markupp(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🔴 {_['P_B_3']}",
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"✖ {_['CLOSEMENU_BUTTON']}",
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"🔴 {_['P_B_3']}",
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🔎 SLIDER MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def slider_markupp(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {query}|{user_id}"
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"🎵 {_['P_B_1']}",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"🎬 {_['P_B_2']}",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=f"✖ {_['CLOSE_BUTTON']}",
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         📋 QUEUE MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def queue_markupp(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text="✖ ᴄʟᴏsᴇ ✖", callback_data="close")],
    ]
    return buttons


def queue_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="‣‣I sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⚙️ ᴍᴏʀᴇ",
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎼 MAIN STREAM MARKUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def stream_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="✚ ᴘʟᴀʏʟɪsᴛ", callback_data=f"vip_playlist {videoid}"),
            InlineKeyboardButton(text="⚙️ ᴄᴏɴᴛʀᴏʟs", callback_data=f"Pages Back|3|{videoid}|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="📥 ᴠɪᴅᴇᴏ", callback_data=f"downloadvideo {videoid}"),
            InlineKeyboardButton(text="📥 ᴀᴜᴅɪᴏ", callback_data=f"downloadaudio {videoid}"),
        ],
        [
            InlineKeyboardButton(
                text="🚀 ᴀᴅᴠᴀɴᴄᴇ",
                callback_data=f"Pages Forw|0|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def stream_markup2(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


def stream_markup_timer(_, videoid, chat_id, played, dur):
    bar = get_progress_bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"🕐 {played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="‣‣I sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🏠 ғᴇᴀᴛᴜʀᴇs",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def stream_markup_timer2(_, chat_id, played, dur):
    bar = get_progress_bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🕐 {played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=f"✖ {_['CLOSEMENU_BUTTON']}", callback_data="close")],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎛️ PANEL MARKUPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def panel_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="‣‣I sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🏠 ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⚡ ɴᴇxᴛ",
                callback_data=f"Pages Forw|0|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_1(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🔀 sᴜғғʟᴇ", callback_data=f"ADMIN Shuffle|{chat_id}"),
            InlineKeyboardButton(text="🔄 ʟᴏᴏᴘ", callback_data=f"ADMIN Loop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="⏪ 10s", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton(text="10s ⏩", callback_data=f"ADMIN 2|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🏠 ʜᴏᴍᴇ",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⚡ ɴᴇxᴛ",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🐢 0.5x", callback_data=f"SpeedUP {chat_id}|0.5"),
            InlineKeyboardButton(text="🎯 1.0x", callback_data=f"SpeedUP {chat_id}|1.0"),
            InlineKeyboardButton(text="⚡ 2.0x", callback_data=f"SpeedUP {chat_id}|2.0"),
        ],
        [
            InlineKeyboardButton(text="🔇 ᴍᴜᴛᴇ", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(text="🔊 ᴜɴᴍᴜᴛᴇ", callback_data=f"ADMIN Unmute|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ ʙᴀᴄᴋ",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🐢 0.5x", callback_data=f"SpeedUP {chat_id}|0.5"),
            InlineKeyboardButton(text="🎯 1.0x", callback_data=f"SpeedUP {chat_id}|1.0"),
            InlineKeyboardButton(text="⚡ 2.0x", callback_data=f"SpeedUP {chat_id}|2.0"),
        ],
        [
            InlineKeyboardButton(text="🔇 ᴍᴜᴛᴇ", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(text="🔊 ᴜɴᴍᴜᴛᴇ", callback_data=f"ADMIN Unmute|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ ʙᴀᴄᴋ",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_5(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="‣‣I sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🏠 ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⚡ ɴᴇxᴛ",
                callback_data=f"Pages Forw|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_4(_, vidid, chat_id, played, dur):
    bar = get_progress_bar(played, dur)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🕐 {played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="II ᴘᴀᴜsᴇ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▢ sᴛᴏᴘ", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="‣‣I sᴋɪᴘ", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷ ʀᴇsᴜᴍᴇ", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="↻ ʀᴇᴘʟᴀʏ", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🏠 ʜᴏᴍᴇ",
                callback_data=f"MainMarkup {vidid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_clone(_, vidid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="📥 ᴠɪᴅᴇᴏ", callback_data=f"downloadvideo {vidid}"),
            InlineKeyboardButton(text="📥 ᴀᴜᴅɪᴏ", callback_data=f"downloadaudio {vidid}"),
        ],
        [
            InlineKeyboardButton(text="✚ ᴘʟᴀʏʟɪsᴛ", callback_data=f"vip_playlist {vidid}"),
        ],
    ]
    return buttons


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🔒 CLOSE BUTTONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text="✖ ᴄʟᴏsᴇ ✖", callback_data="close")]]
)


def close_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"✖ {_['CLOSE_BUTTON']}",
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl
