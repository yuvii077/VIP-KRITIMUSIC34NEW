import asyncio
import re
import logging
import aiohttp
import yt_dlp
from typing import Union, Optional, Tuple, List
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from RishuMusic.utils.formatters import time_to_seconds
from RishuMusic import LOGGER

# --- CONFIGURATION ---
from config import API_ID, BOT_TOKEN, MONGO_DB_URI, YOUTUBE_IMG_URL

# --- SECURITY FILTER ---
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.msg)
        patterns = [r"\d{8,10}:[a-zA-Z0-9_-]{35,}", r"mongodb\+srv://\S+"]
        for pattern in patterns:
            msg = re.sub(pattern, "[PROTECTED]", msg)
        record.msg = msg
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

API_URL = "https://youtube-mini.up.railway.app"

# --- UTILS ---
def get_clean_id(link: str) -> Optional[str]:
    if "v=" in link:
        video_id = link.split('v=')[-1].split('&')[0]
    elif "youtu.be/" in link:
        video_id = link.split('youtu.be/')[-1].split('?')[0]
    else:
        video_id = link
    clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', video_id)
    return clean_id if 5 <= len(clean_id) <= 15 else None


def extract_url_from_info(info: dict, prefer_video: bool = False) -> Optional[str]:
    """Extracts the best playable stream URL from yt-dlp info dict."""
    try:
        # 1. Check direct URL
        if info.get("url"):
            return info["url"]

        # 2. Check requested formats
        requested = info.get("requested_formats")
        if requested:
            if not prefer_video:
                # Sirf audio chahiye
                for fmt in requested:
                    if fmt.get("acodec") != "none" and fmt.get("vcodec") == "none" and fmt.get("url"):
                        return fmt["url"]
                # Agar pure audio na mile toh koi bhi audio wala
                for fmt in requested:
                    if fmt.get("acodec") != "none" and fmt.get("url"):
                        return fmt["url"]
            else:
                # Video chahiye
                for fmt in requested:
                    if fmt.get("vcodec") != "none" and fmt.get("url"):
                        return fmt["url"]

        # 3. Fallback: formats list se
        formats = info.get("formats", [])
        if not prefer_video:
            # Pure audio formats (no video)
            audio_formats = [
                f for f in formats
                if f.get("acodec") != "none"
                and f.get("vcodec") == "none"
                and f.get("url")
            ]
            if audio_formats:
                # Sabse best audio (last = highest quality)
                return audio_formats[-1]["url"]

            # Pure audio na mile toh audio+video mein se audio wala
            mixed = [
                f for f in formats
                if f.get("acodec") != "none" and f.get("url")
            ]
            if mixed:
                return mixed[-1]["url"]
        else:
            # Video formats
            video_formats = [
                f for f in formats
                if f.get("vcodec") != "none" and f.get("url")
            ]
            if video_formats:
                return video_formats[-1]["url"]

        # Last resort
        if formats and formats[-1].get("url"):
            return formats[-1]["url"]

    except Exception as e:
        LOGGER.error(f"Extraction error: {e}")
    return None


async def get_direct_stream_link(link: str, media_type: str) -> Optional[str]:
    video_id = get_clean_id(link)
    if not video_id:
        return None
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(
            headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout
        ) as session:
            async with session.get(
                f"{API_URL}/download",
                params={"url": video_id, "type": media_type}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data.get("download_token")
                    if token:
                        return f"{API_URL}/stream/{video_id}?type={media_type}&token={token}"
    except Exception:
        pass
    return None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str):
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Optional[str]:
        messages = [message, message.reply_to_message]
        for msg in messages:
            if not msg:
                continue
            text = msg.text or msg.caption
            if not text:
                continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset: entity.offset + entity.length]
            urls = re.findall(r'(https?://\S+)', text)
            if urls:
                return urls[0]
        return None

    async def search(self, query: str, limit: int = 1):
        try:
            search = VideosSearch(query, limit=limit)
            resp = await search.next()
            return resp.get("result", [])
        except Exception as e:
            LOGGER.error(f"Search Error: {e}")
            return []

    async def details(self, query: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + query if not query.startswith("http") else query
        else:
            link = query

        try:
            if await self.exists(link):
                ydl_opts = {"quiet": True, "no_warnings": True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = await asyncio.to_thread(ydl.extract_info, link, download=False)
                    title = info.get("title", "Unknown Title")
                    duration_sec = info.get("duration", 0)
                    duration_min = f"{duration_sec // 60:02d}:{duration_sec % 60:02d}"
                    thumbnail = info.get("thumbnail") or YOUTUBE_IMG_URL
                    vidid = info.get("id")
                    return title, duration_min, duration_sec, thumbnail, vidid

            res = await self.search(link, limit=1)
            if not res:
                return None

            video = res[0]
            thumbnail = (
                video.get("thumbnails")[0]["url"].split("?")[0]
                if video.get("thumbnails")
                else YOUTUBE_IMG_URL
            )
            return (
                video.get("title", "Unknown Title"),
                video.get("duration", "00:00"),
                int(time_to_seconds(video.get("duration", "00:00"))),
                thumbnail,
                video.get("id"),
            )
        except Exception as e:
            LOGGER.error(f"Details Error: {e}")
            return None

    async def track(self, query: str, videoid: Union[bool, str] = None):
        det = await self.details(query, videoid)
        if not det:
            return None, None
        track_details = {
            "title": det[0],
            "link": self.base + det[4],
            "vidid": det[4],
            "duration_min": det[1],
            "duration_sec": det[2],
            "thumb": det[3],
        }
        return track_details, det[4]

    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        **kwargs,
    ) -> Tuple[Optional[str], bool]:

        if videoid:
            link = self.base + link

        # /play = audio only | /vplay = video
        is_video = bool(video)
        m_type = "video" if is_video else "audio"

        LOGGER.info(f"[DOWNLOAD] type={m_type} | link={link}")

        # 1. Pehle Railway API try karo
        stream_link = await get_direct_stream_link(link, m_type)
        if stream_link:
            LOGGER.info(f"[DOWNLOAD] API stream mil gaya: {stream_link[:60]}")
            return stream_link, True

        # 2. yt-dlp fallback
        try:
            if is_video:
                fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                # AUDIO ONLY format - video nahi chahiye
                fmt = "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "quiet": True,
                "no_warnings": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "noplaylist": True,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.google.com/",
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, link, download=False)
                if not info:
                    return None, False

            url = extract_url_from_info(info, prefer_video=is_video)

            if url and len(url) > 10:
                LOGGER.info(f"[DOWNLOAD] yt-dlp stream OK | type={m_type}")
                return url, True

        except Exception as e:
            LOGGER.error(f"[DOWNLOAD] yt-dlp error: {e}")

        LOGGER.error(f"[DOWNLOAD] Sab fail ho gaya: {link}")
        return None, False


# Global Instance
YouTube = YouTubeAPI()
