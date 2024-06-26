# https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html

import hashlib
import binascii
import torrent_parser
from pathlib import Path
from qbittorrentapi import Client
from nonebot.utils import run_sync

from .models import TorrentInfo
from .exceptions import TorrentExistsError, TorrentUnexistsError


class TorrentDownloader:
    def __init__(self, host: str, username: str, password: str, download_path: Path):
        self.client = Client(host=host, username=username, password=password)
        self.download_path = download_path

    def _get_torrent_hash(self, torrent_file: bytes):
        torrent = torrent_parser.TorrentFileParser(torrent_file, hash_raw=True).parse()
        info_bytes = torrent_parser.encode(torrent["info"])
        info_hash = binascii.hexlify(hashlib.sha1(info_bytes).digest()).decode()
        return info_hash

    async def download_torrent(
        self, torrent_file: bytes, folder_name: str
    ) -> TorrentInfo:
        hash_str = self._get_torrent_hash(torrent_file)

        if (await self.is_torrent_exists(hash_str)):
            raise TorrentExistsError(f"Torrent with hash {hash_str} already exists.")

        text = await run_sync(self.client.torrents_add)(
            torrent_files=torrent_file, save_path=self.download_path / folder_name
        )

        if text == "Fails.":
            raise Exception("Failed to download torrent.")

        await run_sync(self.client.torrents_reannounce)(torrent_hashes=hash_str)

        torrent_info = (
            await run_sync(self.client.torrents_info)(torrent_hashes=hash_str)
        )[0]

        return torrent_info

    async def is_torrent_exists(self, hash_str: str) -> bool:
        torrents = await run_sync(self.client.torrents_info)(torrent_hashes=hash_str)
        return torrents != []

    async def get_torrent_info(self, hash_str: str) -> TorrentInfo:
        torrents = await run_sync(self.client.torrents_info)(torrent_hashes=hash_str)
        if torrents == []:
            raise TorrentUnexistsError(f"Torrent with hash {hash_str} does not exist.")
        return torrents[0]
