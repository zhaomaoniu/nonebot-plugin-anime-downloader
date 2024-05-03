from typing import List
from pathlib import Path
from nonebot.log import logger
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class VideoManager:
    def __init__(self, app: FastAPI, download_path: Path):
        if not isinstance(app, FastAPI):
            raise TypeError("app must be an instance of FastAPI.")

        self.ids: List[int] = []
        self.app = app
        self.download_path = download_path
        self.templates = Jinja2Templates(
            directory=(Path(__file__).parent / "templates").resolve()
        )

        app.mount(
            "/video",
            StaticFiles(directory=download_path.resolve()),
            name="video",
        )

    def add_route(self, video_path: Path, torrent_id: int) -> None:
        self.ids.append(torrent_id)

        @self.app.get(f"/anime/{torrent_id}")
        async def anime_display(request: Request):
            return self.templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "title": video_path.name,
                    "video_path": f"/{video_path.parent.name}/{video_path.name}",
                    "video_type": f"video/{video_path.suffix[1:]}",
                },
            )

        logger.success(f"Added route for video {video_path.name}.")
