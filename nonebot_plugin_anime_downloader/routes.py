from typing import List
from pathlib import Path
from nonebot.log import logger
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse


class VideoManager:
    def __init__(self, app: FastAPI, download_path: Path):
        if not isinstance(app, FastAPI):
            raise TypeError("app must be an instance of FastAPI.")

        self.ids: List[int] = []
        self.app = app
        self.download_path = download_path
        self.templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

    def add_route(self, video_path: Path, torrent_id: int) -> None:
        if torrent_id in self.ids:
            return None

        self.ids.append(torrent_id)

        @self.app.get(f"/anime/{torrent_id}")
        async def anime_page(request: Request):
            return self.templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "title": video_path.name,
                    "video_url": f"/res/{torrent_id}",
                    "mime_type": f"video/{video_path.suffix[1:]}",
                },
            )

        @self.app.get(f"/res/{torrent_id}")
        async def anime_res(request: Request):
            file_size = video_path.stat().st_size
            start, end = 0, file_size - 1
            range_header = request.headers.get("Range")
            if range_header:
                start, end = range_header.replace("bytes=", "").split("-")
                start = int(start)
                end = int(end) if end else file_size - 1
                status_code = 206
            else:
                status_code = 200

            def iterfile():
                with open(video_path, mode="rb") as file_like:
                    file_like.seek(start)
                    bytes_to_send = end - start + 1
                    while bytes_to_send > 0:
                        chunk_size = min(
                            bytes_to_send, 1024 * 1024
                        )  # 1MB chunks or less
                        data = file_like.read(chunk_size)
                        if not data:
                            break
                        yield data
                        bytes_to_send -= len(data)

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
                "Content-Type": f"video/{video_path.suffix[1:]}",
            }

            return StreamingResponse(
                iterfile(),
                status_code=status_code,
                headers=headers,
                media_type=f"video/{video_path.suffix[1:]}",
            )

    def add_routes(self, video_paths: List[Path], torrent_ids: List[int]) -> None:
        for video_path, torrent_id in zip(video_paths, torrent_ids):
            self.add_route(video_path, torrent_id)

        logger.success(f"Added routes for {len(video_paths)} videos.")
