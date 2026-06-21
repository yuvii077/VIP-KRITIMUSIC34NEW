import asyncio
import re
import logging
import json
import aiohttp
from typing import Union, Optional, Tuple, List
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from VIPMUSIC import LOGGER

# --- CONFIGURATION ---
from config import YOUTUBE_IMG_URL

# ─── SECURITY FILTER ──────────────────────────────────────────────────────────
class SensitiveDataFilter(logging.Filter):
    """Logs mein se sensitive data (tokens, DB URLs) filter karta hai."""
    def filter(self, record):
        msg = str(record.msg)
        patterns = [
            r"\d{8,10}:[a-zA-Z0-9_-]{35,}",  # Telegram bot token
            r"mongodb\+srv://\S+",             # MongoDB URI
            r"xbit_[a-zA-Z0-9_-]+",            # API key
        ]
        for pattern in patterns:
            msg = re.sub(pattern, "[PROTECTED]", msg)
        record.msg = msg
        return True

logging.getLogger().addFilter(SensitiveDataFilter())

# ─── VIP-MUSIC API CONFIG ─────────────────────────────────────────────────────
API_BASE = "https://tgapi.xbitcode.com"
API_KEY = "xbit_QuWntW2N_YmM2lSa2k2MRk3s-k0ONA-0"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

# ─── DURATION PARSER ──────────────────────────────────────────────────────────
def parse_duration(duration_str) -> Tuple[str, int]:
    """
    Duration string (HH:MM:SS / MM:SS / SS) ko parse karke
    (formatted_str, total_seconds) return karta hai.
    """
    if not duration_str:
        return "00:00", 0
    try:
        parts = [int(p) for p in str(duration_str).strip().split(":")]
        if len(parts) == 1:
            secs = parts[0]
        elif len(parts) == 2:
            secs = parts[0] * 60 + parts[1]
        else:
            secs = parts[0] * 3600 + parts[1] * 60 + parts[2]
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if h:
            return f"{h:02d}:{m:02d}:{s:02d}", secs
        return f"{m:02d}:{s:02d}", secs
    except Exception:
        return "00:00", 0


# ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────
def get_clean_id(link: str) -> Optional[str]:
    """
    YouTube link ya video ID se clean video ID extract karta hai.
    Returns None agar valid ID nahi mila.
    """
    if not link:
        return None
    link = link.strip()

    if "v=" in link:
        video_id = link.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in link:
        video_id = link.split("youtu.be/")[-1].split("?")[0]
    elif "youtube.com/embed/" in link:
        video_id = link.split("youtube.com/embed/")[-1].split("?")[0]
    elif "youtube.com/shorts/" in link:
        video_id = link.split("youtube.com/shorts/")[-1].split("?")[0]
    else:
        video_id = link

    clean_id = re.sub(r"[^a-zA-Z0-9_-]", "", video_id)

    return clean_id if 5 <= len(clean_id) <= 15 else None


async def api_get(endpoint: str, params: dict = None) -> Optional[dict]:
    """
    API_BASE pe GET request bhejta hai aur JSON response return karta hai.
    Failure pe None return karta hai.
    """
    if params is None:
        params = {}

    url = f"{API_BASE}/{endpoint}"
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:
            async with session.get(url, params=params) as resp:
                text = await resp.text()
                LOGGER(__name__).debug(
                    f"[API] {url} | params={params} | "
                    f"status={resp.status} | response={text[:300]}"
                )
                if resp.status == 200:
                    return json.loads(text)
                LOGGER(__name__).warning(
                    f"[API] Non-200 status {resp.status} for {endpoint}"
                )
    except aiohttp.ClientConnectorError:
        LOGGER(__name__).error(f"[API] Connection failed: {API_BASE}")
    except asyncio.TimeoutError:
        LOGGER(__name__).error(f"[API] Timeout: {endpoint}")
    except json.JSONDecodeError as e:
        LOGGER(__name__).error(f"[API] Invalid JSON from {endpoint}: {e}")
    except Exception as e:
        LOGGER(__name__).error(f"[API] Unexpected error {endpoint}: {e}")
    return None


# ─── AUDIO STREAM FETCHER ─────────────────────────────────────────────────────
async def get_audio_stream_url(video_id: str) -> Optional[str]:
    """
    Diye gaye video_id ke liye sirf AUDIO stream URL fetch karta hai.
    """
    data = await api_get("api/yt/stream", {"id": video_id, "type": "audio"})
    if data:
        stream = (
            data.get("audio")
            or data.get("stream")
            or data.get("url")
            or data.get("audioUrl")
            or data.get("audio_url")
        )
        if stream:
            LOGGER(__name__).info(
                f"[AUDIO] Stream mila (audio type): {video_id}"
            )
            return stream

    LOGGER(__name__).debug(
        f"[AUDIO] Audio type nahi mila, generic stream try kar raha hoon: {video_id}"
    )
    data = await api_get("api/yt/stream", {"id": video_id})
    if data:
        stream = (
            data.get("audio")
            or data.get("stream")
            or data.get("url")
            or data.get("audioUrl")
        )
        if stream:
            LOGGER(__name__).info(
                f"[AUDIO] Stream mila (generic fallback): {video_id}"
            )
            return stream

    LOGGER(__name__).warning(f"[AUDIO] Koi bhi stream nahi mila: {video_id}")
    return None


# ─── SEARCH HELPER ────────────────────────────────────────────────────────────
async def search_api(query: str, limit: int = 1) -> List[dict]:
    """
    API se YouTube search results fetch karta hai.
    """
    data = await api_get("api/yt/search", {"q": query, "max": limit})
    if data and isinstance(data.get("results"), list):
        return data["results"]
    return []


# ─── YouTubeAPI CLASS ─────────────────────────────────────────────────────────
class YouTubeAPI:
    """
    YouTube audio streaming ke liye complete API wrapper.
    Koi file download nahi hoti — seedha stream URLs use hoti hain.
    """

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"

    async def exists(self, link: str) -> bool:
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
                        url_text = text[entity.offset: entity.offset + entity.length]
                        if re.search(self.regex, url_text):
                            return url_text
            urls = re.findall(r"(https?://\S+)", text)
            for u in urls:
                if re.search(self.regex, u):
                    return u
        return None

    async def details(
        self, query: str, videoid: Union[bool, str] = None
    ) -> Optional[Tuple[str, str, int, str, str]]:
        LOGGER(__name__).debug(
            f"[DETAILS] query={query!r} | videoid={videoid!r}"
        )

        video_id = None

        if videoid:
            video_id = get_clean_id(query) or query.strip()
        elif await self.exists(query):
            video_id = get_clean_id(query)

        LOGGER(__name__).debug(f"[DETAILS] Resolved video_id={video_id!r}")

        if video_id:
            stream_data = await api_get("api/yt/stream", {"id": video_id})
            LOGGER(__name__).debug(f"[DETAILS] stream_data={stream_data}")

            if stream_data and (
                stream_data.get("stream")
                or stream_data.get("audio")
                or stream_data.get("url")
            ):
                title = stream_data.get("title") or "Unknown Title"
                thumb = stream_data.get("thumb") or YOUTUBE_IMG_URL

                dur_str, dur_sec = "00:00", 0
                if stream_data.get("duration"):
                    dur_str, dur_sec = parse_duration(stream_data["duration"])
                else:
                    search_res = await search_api(title, limit=1)
                    if search_res:
                        dur_str, dur_sec = parse_duration(
                            search_res[0].get("duration", "0:00")
                        )

                LOGGER(__name__).debug(
                    f"[DETAILS] Direct hit: {title} | {video_id} | {dur_str}"
                )
                return title, dur_str, dur_sec, thumb, video_id

        LOGGER(__name__).debug(
            f"[DETAILS] Search API try kar raha hoon: {query!r}"
        )
        results = await search_api(query, limit=1)
        LOGGER(__name__).debug(f"[DETAILS] Search results={results}")

        if results:
            v = results[0]
            vid_id = v.get("id", "")
            title = v.get("title") or "Unknown Title"
            thumb = v.get("thumb") or v.get("thumbnail") or YOUTUBE_IMG_URL
            dur_str, dur_sec = parse_duration(v.get("duration", "0:00"))

            LOGGER(__name__).debug(
                f"[DETAILS] Search hit: {title} | {vid_id} | {dur_str}"
            )
            return title, dur_str, dur_sec, thumb, vid_id

        LOGGER(__name__).debug(
            f"[DETAILS] youtubesearchpython fallback try kar raha hoon"
        )
        try:
            search = VideosSearch(query, limit=1)
            resp = await search.next()
            res = resp.get("result", [])
            if res:
                v = res[0]
                thumbnails = v.get("thumbnails") or [{}]
                thumb = thumbnails[0].get("url", YOUTUBE_IMG_URL).split("?")[0]
                dur_str, dur_sec = parse_duration(v.get("duration", "0:00"))
                vid_id = v.get("id", "")
                title = v.get("title") or "Unknown Title"

                LOGGER(__name__).debug(
                    f"[DETAILS] Fallback hit: {title} | {vid_id} | {dur_str}"
                )
                return title, dur_str, dur_sec, thumb, vid_id
        except Exception as e:
            LOGGER(__name__).error(f"[DETAILS] Fallback error: {e}")

        LOGGER(__name__).warning(
            f"[DETAILS] Sabhi methods fail ho gaye: {query!r}"
        )
        return None

    async def track(
        self, query: str, videoid: Union[bool, str] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        det = await self.details(query, videoid)
        if not det:
            LOGGER(__name__).warning(
                f"[TRACK] Details nahi mili: {query!r}"
            )
            return None, None

        title, dur_str, dur_sec, thumb, vid_id = det

        track_details = {
            "title":        title,
            "link":         self.base + vid_id,
            "vidid":        vid_id,
            "duration_min": dur_str,
            "duration_sec": dur_sec,
            "thumb":        thumb,
        }

        LOGGER(__name__).info(
            f"[TRACK] Ready: {title!r} | {vid_id} | {dur_str}"
        )
        return track_details, vid_id

    async def download(
        self,
        link: str,
        mystic=None,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        **kwargs,
    ) -> Tuple[Optional[str], bool]:
        if videoid:
            video_id = get_clean_id(link) or link.strip()
        else:
            video_id = get_clean_id(link)

        if not video_id:
            LOGGER(__name__).warning(
                f"[DOWNLOAD] Invalid/unparseable video ID: {link!r}"
            )
            return None, False

        LOGGER(__name__).info(
            f"[DOWNLOAD] Audio stream fetch kar raha hoon: {video_id}"
        )

        stream_url = await get_audio_stream_url(video_id)

        if stream_url:
            LOGGER(__name__).info(
                f"[DOWNLOAD] Audio stream ready: {video_id}"
            )
            return stream_url, True

        LOGGER(__name__).warning(
            f"[DOWNLOAD] Audio stream nahi mila: {video_id}"
        )
        return None, False


# ─── GLOBAL INSTANCE ──────────────────────────────────────────────────────────
YouTube = YouTubeAPI()
