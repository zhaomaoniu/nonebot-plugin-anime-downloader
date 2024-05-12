from typing import TypedDict

from .downloader.models import TorrentInfo


class Task(TypedDict):
    id: str  # group/private_id
    content: TorrentInfo
    torrent_id: int
    status: str
