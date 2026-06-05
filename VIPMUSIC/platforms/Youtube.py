import asyncio
import logging
import re
from typing import Union

import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from VIPMUSIC.utils.database import is_on_off

# ─── Logger setup ────────────────────────────────────────────────────────────
LOGGER = logging.getLogger("YouTubeAPI")

# ─── Invidious public instances — fallback order mein ────────────────────────
INVIDIOUS_INSTANCES = [
    "https://invidious.f5.si",        # primary — working ✓
    "https://inv.nadeko.net",
    "https://invidious.privacyredirect.com",
    "https://invidious.einfachzocken.eu",
    "https://iv.datura.network",
    "https://invidious.fdn.fr",
]
# ─────────────────────────────────────────────────────────────────────────────

_SESSION: aiohttp.ClientSession | None = None


async def _get_session() -> aiohttp.ClientSession:
    global _SESSION
    if _SESSION is None or _SESSION.closed:
        _SESSION = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={"User-Agent": "Mozilla/5.0"},
        )
    return _SESSION


async def _api_get(path: str, params: dict = None) -> dict | list | None:
    """
    Saare instances try karo — jo pehla kaam kare uska result return karo.
    Sab fail ho jaaye toh None return karo.
    """
    session = await _get_session()
    for base in INVIDIOUS_INSTANCES:
        url = f"{base}/api/v1/{path}"
        try:
            async with session.get(url, params=params) as resp:
                LOGGER.debug("[Invidious] %s → HTTP %s", url, resp.status)
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data:
                        LOGGER.debug("[Invidious] SUCCESS: %s", base)
                        return data
                else:
                    LOGGER.warning(
                        "[Invidious] HTTP %s from %s | path=%s params=%s",
                        resp.status, base, path, params,
                    )
        except asyncio.TimeoutError:
            LOGGER.warning("[Invidious] TIMEOUT: %s | path=%s", base, path)
        except aiohttp.ClientConnectorError as e:
            LOGGER.warning("[Invidious] CONNECT ERROR: %s | %s", base, e)
        except Exception as e:
            LOGGER.warning("[Invidious] ERROR: %s | %s: %s", base, type(e).__name__, e)

    LOGGER.error(
        "[Invidious] ALL instances FAILED for path=%s params=%s", path, params
    )
    return None


def _seconds_to_mmss(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"


def _best_thumbnail(thumbnails: list) -> str:
    if not thumbnails:
        return ""
    for q in ("maxres", "maxresdefault", "sddefault", "high", "medium", "default", "start", "middle", "end"):
        for t in thumbnails:
            if t.get("quality") == q:
                return t.get("url", "")
    return thumbnails[0].get("url", "")


def _best_stream_url(data: dict, prefer_video: bool = False) -> str | None:
    if prefer_video:
        streams = data.get("formatStreams", [])
        for res in ("720p", "480p", "360p", "240p"):
            for s in streams:
                if s.get("resolution") == res:
                    return s.get("url")
        if streams:
            return streams[0].get("url")
    else:
        adaptive = data.get("adaptiveFormats", [])
        audio_streams = [
            s for s in adaptive
            if s.get("audioQuality") and not s.get("resolution")
        ]
        if audio_streams:
            best = max(audio_streams, key=lambda s: int(s.get("bitrate") or 0))
            return best.get("url")
    return None


def _empty_track() -> dict:
    return {
        "title": "",
        "link": "",
        "vidid": "",
        "duration_min": None,
        "duration_sec": 0,
        "thumb": "",
    }


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _extract_videoid(self, link: str) -> str | None:
        match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", link)
        return match.group(1) if match else None

    def _clean_link(self, link: str) -> str:
        if "&" in link:
            link = link.split("&")[0]
        return link.strip()

    async def _search_first(self, query: str) -> dict | None:
        LOGGER.info("[Search] query='%s'", query)
        results = await _api_get("search", {"q": query, "type": "video", "page": 1, "region": "IN"})
        if isinstance(results, list):
            for item in results:
                if item.get("type") == "video":
                    LOGGER.info(
                        "[Search] Found: '%s' | id=%s",
                        item.get("title"), item.get("videoId"),
                    )
                    return item
        LOGGER.error("[Search] No results for query='%s'", query)
        return None

    async def _get_video_data(self, link: str) -> tuple[dict | None, str]:
        link = self._clean_link(link)
        vid = self._extract_videoid(link)
        LOGGER.info("[GetVideoData] link='%s' | extracted_id=%s", link, vid)

        data = None
        if vid:
            LOGGER.info("[GetVideoData] Fetching video info for id=%s", vid)
            data = await _api_get(f"videos/{vid}")
            if not data:
                LOGGER.warning("[GetVideoData] Direct video fetch failed for id=%s", vid)

        if not data:
            LOGGER.info("[GetVideoData] Falling back to search for '%s'", link)
            search_result = await self._search_first(link)
            if not search_result:
                LOGGER.error("[GetVideoData] Search also failed for '%s'", link)
                return None, ""
            vid = search_result.get("videoId", "")
            LOGGER.info("[GetVideoData] Search gave id=%s, fetching full info...", vid)
            full = await _api_get(f"videos/{vid}")
            if full:
                data = full
                LOGGER.info("[GetVideoData] Full video info fetched for id=%s", vid)
            else:
                LOGGER.warning(
                    "[GetVideoData] Full fetch failed, using search result for id=%s", vid
                )
                data = search_result

        vid = vid or data.get("videoId", "")
        LOGGER.info(
            "[GetVideoData] Final: id=%s | title='%s'",
            vid, data.get("title", "N/A"),
        )
        return data, vid

    # ─── Public API methods ──────────────────────────────────────────────────

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        offset = None
        length = None
        text = ""
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        LOGGER.info("[details] link='%s'", link)
        data, vid = await self._get_video_data(link)
        if not data:
            LOGGER.error("[details] FAILED for link='%s'", link)
            return None, None, None, None, None
        title      = data.get("title", "")
        length_sec = int(data.get("lengthSeconds", 0))
        dur_min    = _seconds_to_mmss(length_sec)
        thumb      = _best_thumbnail(data.get("videoThumbnails", []))
        LOGGER.info("[details] OK: title='%s' dur=%s", title, dur_min)
        return title, dur_min, length_sec, thumb, vid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        data, _ = await self._get_video_data(link)
        return data.get("title", "") if data else ""

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        data, _ = await self._get_video_data(link)
        if not data:
            return "0:00"
        return _seconds_to_mmss(int(data.get("lengthSeconds", 0)))

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        data, _ = await self._get_video_data(link)
        if not data:
            return ""
        return _best_thumbnail(data.get("videoThumbnails", []))

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        LOGGER.info("[video] link='%s'", link)
        data, vid = await self._get_video_data(link)
        if not data:
            LOGGER.error("[video] FAILED: no data for link='%s'", link)
            return 0, "Invidious se video info nahi mili"
        url = _best_stream_url(data, prefer_video=True)
        if url:
            LOGGER.info("[video] Stream URL found for id=%s", vid)
            return 1, url
        if data.get("hlsUrl"):
            LOGGER.info("[video] Using hlsUrl for id=%s", vid)
            return 1, data["hlsUrl"]
        LOGGER.error("[video] No stream URL found for id=%s", vid)
        return 0, "Stream URL nahi mili"

    async def playlist(self, link: str, limit: int, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        link = self._clean_link(link)
        match = re.search(r"list=([A-Za-z0-9_-]+)", link)
        plid = match.group(1) if match else link
        LOGGER.info("[playlist] plid=%s limit=%s", plid, limit)

        video_ids = []
        page = 1
        while len(video_ids) < limit:
            data = await _api_get(f"playlists/{plid}", {"page": page})
            if not data or not data.get("videos"):
                LOGGER.warning("[playlist] No videos on page=%s for plid=%s", page, plid)
                break
            for v in data["videos"]:
                if len(video_ids) >= limit:
                    break
                vid = v.get("videoId")
                if vid:
                    video_ids.append(vid)
            if len(data["videos"]) < 100:
                break
            page += 1

        LOGGER.info("[playlist] Got %s video IDs for plid=%s", len(video_ids), plid)
        return video_ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        LOGGER.info("[track] link='%s'", link)

        data, vid = await self._get_video_data(link)

        if not data or not vid:
            LOGGER.error("[track] FAILED: no data/vid for link='%s'", link)
            return _empty_track(), None

        title      = data.get("title", "")
        length_sec = int(data.get("lengthSeconds", 0))
        dur_min    = _seconds_to_mmss(length_sec) if length_sec else None
        thumb      = _best_thumbnail(data.get("videoThumbnails", []))
        yturl      = f"https://www.youtube.com/watch?v={vid}"

        LOGGER.info(
            "[track] OK: title='%s' | id=%s | dur=%s | thumb=%s",
            title, vid, dur_min, bool(thumb),
        )

        return {
            "title":        title,
            "link":         yturl,
            "vidid":        vid,
            "duration_min": dur_min,
            "duration_sec": length_sec,
            "thumb":        thumb,
        }, vid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        LOGGER.info("[formats] link='%s'", link)
        data, vid = await self._get_video_data(link)
        if not data:
            LOGGER.error("[formats] FAILED for link='%s'", link)
            return [], link

        formats_available = []
        for fmt in data.get("formatStreams", []):
            formats_available.append({
                "format":      f"{fmt.get('qualityLabel', '')} ({fmt.get('container', '')})",
                "filesize":    None,
                "format_id":  fmt.get("itag", ""),
                "ext":         fmt.get("container", ""),
                "format_note": fmt.get("qualityLabel", ""),
                "yturl":       fmt.get("url", ""),
            })
        for fmt in data.get("adaptiveFormats", []):
            label = fmt.get("qualityLabel") or fmt.get("audioQuality") or ""
            if not label:
                continue
            formats_available.append({
                "format":      f"{label} ({fmt.get('container', '')})",
                "filesize":    fmt.get("clen"),
                "format_id":  fmt.get("itag", ""),
                "ext":         fmt.get("container", ""),
                "format_note": label,
                "yturl":       fmt.get("url", ""),
            })

        LOGGER.info("[formats] Found %s formats for id=%s", len(formats_available), vid)
        return formats_available, f"https://www.youtube.com/watch?v={vid}"

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        link = self._clean_link(link)
        LOGGER.info("[slider] query='%s' index=%s", link, query_type)

        results = await _api_get("search", {"q": link, "type": "video", "page": 1, "region": "IN"})
        videos  = [r for r in (results or []) if r.get("type") == "video"]

        if not videos or query_type >= len(videos):
            LOGGER.error(
                "[slider] Not enough results for query='%s' index=%s (got %s)",
                link, query_type, len(videos),
            )
            return None, None, None, None

        item      = videos[query_type]
        title     = item.get("title", "")
        vid       = item.get("videoId", "")
        dur_min   = _seconds_to_mmss(int(item.get("lengthSeconds", 0)))
        thumb     = _best_thumbnail(item.get("videoThumbnails", []))
        LOGGER.info("[slider] Result[%s]: '%s' id=%s", query_type, title, vid)
        return title, dur_min, thumb, vid

    async def download(
        self,
        link: str,
        mystic,
        video:     Union[bool, str] = None,
        videoid:   Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title:     Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        LOGGER.info(
            "[download] link='%s' | video=%s songaudio=%s songvideo=%s format_id=%s",
            link, video, songaudio, songvideo, format_id,
        )

        data, vid = await self._get_video_data(link)
        if not data:
            LOGGER.error("[download] FAILED: no data for link='%s'", link)
            return None, None

        all_formats = data.get("adaptiveFormats", []) + data.get("formatStreams", [])

        if songvideo or (video and await is_on_off(1)):
            if format_id:
                for fmt in all_formats:
                    if str(fmt.get("itag")) == str(format_id):
                        LOGGER.info("[download] songvideo: found itag=%s", format_id)
                        return fmt["url"], True
            url = _best_stream_url(data, prefer_video=True) or data.get("hlsUrl")
            LOGGER.info("[download] songvideo fallback url=%s", bool(url))
            return url, True

        elif songaudio:
            if format_id:
                for fmt in data.get("adaptiveFormats", []):
                    if str(fmt.get("itag")) == str(format_id):
                        LOGGER.info("[download] songaudio: found itag=%s", format_id)
                        return fmt["url"], True
            url = _best_stream_url(data, prefer_video=False)
            LOGGER.info("[download] songaudio best_audio url=%s", bool(url))
            return url, True

        elif video:
            url = _best_stream_url(data, prefer_video=True) or data.get("hlsUrl")
            LOGGER.info("[download] video mode url=%s", bool(url))
            return url, None

        else:
            url = _best_stream_url(data, prefer_video=False)
            LOGGER.info("[download] audio-only url=%s", bool(url))
            return url, True
