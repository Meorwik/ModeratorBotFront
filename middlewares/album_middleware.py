from forms.enums import AllowedContentTypes
from typing import Any, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message
import asyncio


class AlbumMedia:
    def __init__(self, caption: str = None, photo=None, video=None):
        self.caption = caption
        self.photo = photo
        self.video = video

    def __repr__(self):
        return f"Cap:{self.caption} - Photo:{self.photo} - Vid:{self.video}"


class MediaFile:

    def __init__(self, file_id: str, content_type: AllowedContentTypes = AllowedContentTypes.unknown):
        self.file_id: str = file_id
        self.content_type: AllowedContentTypes = content_type

    def __repr__(self):
        return f"MediaFile ({self.content_type}) - ({self.file_id})"


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 2):
        self.latency = latency
        self.album_data = {}

    def collect_album_messages(self, event: Message):
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = {"messages": []}

        self.album_data[event.media_group_id]["messages"].append(event)

        return len(self.album_data[event.media_group_id]["messages"])

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        total_before = self.collect_album_messages(event)

        await asyncio.sleep(self.latency)

        total_after = len(self.album_data[event.media_group_id]["messages"])

        if total_before != total_after:
            return

        album_messages = self.album_data[event.media_group_id]["messages"]
        album_messages.sort(key=lambda x: x.message_id)
        album_media = [
            AlbumMedia(
                caption=msg.caption,
                photo=msg.photo[-1].file_id if msg.photo else None,
                video=msg.video.file_id if msg.video else None
            )
            for msg in album_messages if msg.photo
        ]
        data["album"] = album_media

        del self.album_data[event.media_group_id]

        return await handler(event, data)
