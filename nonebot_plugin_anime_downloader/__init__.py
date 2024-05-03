import json
import nonebot
from typing import List
from pathlib import Path
from nonebot import require
from nonebot.log import logger
from nonebot import on_command
from sqlalchemy import create_engine
from nonebot.drivers import ASGIMixin
from sqlalchemy.orm import sessionmaker
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event, Message
from nonebot.params import CommandArg, Depends
from nonebot.plugin import inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")

import nonebot_plugin_localstore as store
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_alconna import UniMessage, Target

from .config import Config
from .tasks import TaskManager
from .routes import VideoManager
from .downloader import TorrentDownloader
from .utils import is_tag_match_title, generate_folder_name
from .data_source import ACGRIPBase, UserBase, VideoBase, ACGRIPData, User, Video
from .acgrip import (
    make_request,
    extract_data,
    fetch_torrent_data,
    replace_html_entities,
)


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_anime_downloader",
    description="基于 qBittorrent Web UI 的番剧下载 NoneBot 插件",
    usage="/sub 订阅 Tag\n/unsub 取消订阅 Tag\n/listsub 查看订阅列表",
    type="application",
    homepage="https://github.com/zhaomaoniu/nonebot-plugin-anime-downloader",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)


if hasattr(nonebot, "get_plugin_config"):
    plugin_config = nonebot.get_plugin_config(Config)
else:
    plugin_config = Config.parse_obj(nonebot.get_driver().config)


download_path = Path(plugin_config.download_path)

if not download_path.exists():
    try:
        download_path.mkdir(parents=True)
    except PermissionError:
        download_path = store.get_data_dir("nonebot_plugin_anime_downloader")
        logger.warning(f"无法创建下载目录！请自行创建下载目录后重启 NoneBot. 本次下载目录为: {download_path}")

tasks_file = store.get_data_file("nonebot_plugin_anime_downloader", "tasks.json")

task_manager = TaskManager(tasks_file)
video_manager = VideoManager(nonebot.get_app(), download_path)

torrent_downloader = TorrentDownloader(
    plugin_config.qbittorrent_host,
    plugin_config.qbittorrent_username,
    plugin_config.qbittorrent_password,
    download_path,
)

acg_rip_file = store.get_data_file("nonebot_plugin_anime_downloader", "acgrip.db")
user_file = store.get_data_file("nonebot_plugin_anime_downloader", "users.db")
video_file = store.get_data_file("nonebot_plugin_anime_downloader", "videos.db")

acg_rip_engine = create_engine(f"sqlite:///{acg_rip_file.resolve()}")
user_engine = create_engine(f"sqlite:///{user_file.resolve()}")
video_engine = create_engine(f"sqlite:///{video_file.resolve()}")

ACGRIPBase.metadata.create_all(acg_rip_engine)
UserBase.metadata.create_all(user_engine)
VideoBase.metadata.create_all(video_engine)

acgrip_session = sessionmaker(bind=acg_rip_engine)()
user_session = sessionmaker(bind=user_engine)()
video_session = sessionmaker(bind=video_engine)()


@scheduler.scheduled_job("interval", seconds=plugin_config.acgrip_interval)
@nonebot.get_driver().on_startup
async def fetch_acgrip_data():
    html_content = await make_request(base_url=plugin_config.acgrip_url)
    data = extract_data(replace_html_entities(html_content))

    # get new data
    new_data = []
    for entry in data:
        if acgrip_session.query(ACGRIPData).filter_by(id=entry["id"]).first() is None:
            new_data.append(entry)

    if new_data == []:
        logger.debug("No new data found.")
        return None

    logger.info(f"ACG.RIP updated with {len(new_data)} new entries.\n{new_data}")

    # store new data
    for entry in new_data:
        acgrip_session.add(ACGRIPData(**entry))
    acgrip_session.commit()

    # check if any user is interested in the new data
    users = user_session.query(User).all()
    for user in users:
        tags_str = user.tags
        tags_list: List[List[str]] = json.loads(tags_str)
        for tags in tags_list:
            for entry in new_data:
                if is_tag_match_title(tags, entry["title"]):
                    # start download torrent
                    logger.info(f"Downloading {entry['title']} for {user.id}...")

                    if str(entry["url"]).startswith("http"):
                        url = f"{entry['url']}.torrent"
                    else:
                        url = f"{plugin_config.acgrip_url}{entry['url']}.torrent"

                    torrent_data = await fetch_torrent_data(url)
                    torrent_info = await torrent_downloader.download_torrent(
                        torrent_data, generate_folder_name(tags)
                    )
                    task_manager.add(
                        {
                            "id": user.id,
                            "content": torrent_info,
                            "torrent_id": int(entry["id"]),
                        }
                    )

                # set a scheduler to check if the video is downloaded
                async def check_video_downloaded(
                    title: str, torrent_id: int, user_id: str
                ):
                    logger.info(
                        f"Checking whether {title} is downloaded for {user_id}..."
                    )
                    if torrent_id in video_manager.ids:
                        logger.info(
                            f"{title} is downloaded for {user_id}! Sending message..."
                        )
                        # send message to user
                        msg = (
                            f"{title} 现在可以观看了！\n"
                            + f"{plugin_config.anime_url}:{nonebot.get_driver().config.port}/anime/{torrent_id}"
                        )
                        chat_type = str(user_id).split("_")[0]
                        id_ = str(user_id).split("_")[-1]
                        target = Target(
                            id=id_,
                            parent_id=id_ if chat_type == "group" else "",
                            channel=chat_type == "group",
                            private=chat_type == "private",
                        )
                        await UniMessage(msg).send(target)
                        logger.info(f"Message sent to {user_id}!")

                        scheduler.remove_job(f"{title}_{user_id}")
                    else:
                        logger.info(f"{title} is not downloaded yet for {user_id}.")

                scheduler.add_job(
                    check_video_downloaded,
                    "interval",
                    seconds=10,
                    args=(entry["title"], int(entry["id"]), user.id),
                    id=f"{entry['title']}_{user.id}",
                )


@scheduler.scheduled_job("interval", seconds=60)
async def check_for_tasks():
    tasks = task_manager.get()

    for task in tasks:
        hash_str = task["content"]["hash"]

        torrent_info = await torrent_downloader.get_torrent_info(hash_str)

        if torrent_info["progress"] != 1:
            logger.info(f"Torrent {task['content']['name']} is not downloaded yet.")
            task_manager.add(
                {
                    "id": task["id"],
                    "content": torrent_info,
                    "torrent_id": task["torrent_id"],
                }
            )
            return None

        logger.success(
            f"Torrent {task['content']['name']} is downloaded, waiting to be added to the route..."
        )

        existing_video = (
            video_session.query(Video).filter_by(id=task["torrent_id"]).first()
        )
        if existing_video is None:
            video_session.add(
                Video(
                    id=task["torrent_id"],
                    title=torrent_info["name"],
                    path=f"{torrent_info['save_path']}\\{torrent_info['name']}",
                )
            )

        video_session.commit()


@scheduler.scheduled_job("interval", seconds=30)
@nonebot.get_driver().on_startup
async def check_for_new_videos():
    videos = video_session.query(Video).all()

    for video in videos:
        if not Path(video.path).exists():
            continue

        video_manager.add_route(Path(video.path), video.id)


@nonebot.get_driver().on_startup
async def on_startup():
    if not isinstance(nonebot.get_driver(), ASGIMixin):
        logger.error("nonebot_plugin_anime_downloader 仅支持 ASGI driver!")
        raise RuntimeError("nonebot_plugin_anime_downloader only supports ASGI driver.")


async def get_target(event: Event) -> Target:
    return UniMessage.get_target(event)


subscribes = on_command("sub", aliases={"订阅"}, priority=5)
unsubscribes = on_command("unsub", aliases={"取消订阅"}, priority=5)
list_subscribes = on_command("listsub", aliases={"订阅列表", "sublist"}, priority=5)
test = on_command("anitest", priority=5)


@subscribes.handle()
async def sub_handle(target: Target = Depends(get_target), arg: Message = CommandArg()):
    if arg.extract_plain_text() == "":
        await subscribes.finish("请提供 Tag！")

    args = arg.extract_plain_text().split(" ")

    if args == []:
        await subscribes.finish("请提供 Tag！")

    # check if the user is already subscribed the same tag
    id_ = f"{'private' if target.private else 'group'}_{target.id}"
    print(id_, target.id, target.private)
    user = user_session.query(User).filter_by(id=id_).first()
    if user is not None:
        tags_str = user.tags
        tags_list: List[List[str]] = json.loads(tags_str)
        for tags in tags_list:
            if tags == args:
                await subscribes.finish("您已经订阅了这个 Tag！")
        tags_list.append(args)
        user.tags = json.dumps(tags_list, ensure_ascii=False)
    else:
        user_session.add(User(id=id_, tags=json.dumps([args], ensure_ascii=False)))
    user_session.commit()
    await subscribes.finish("订阅成功！")


@unsubscribes.handle()
async def unsub_handle(
    target: Target = Depends(get_target), arg: Message = CommandArg()
):
    args = arg.extract_plain_text().split(" ")

    if args == []:
        await unsubscribes.finish("请提供 Tag！")

    id_ = f"{'private' if target.private else 'group'}_{target.id}"
    user = user_session.query(User).filter_by(id=id_).first()
    if user is None:
        await unsubscribes.finish("您还没有订阅任何 Tag！")
    tags_str = user.tags
    tags_list: List[List[str]] = json.loads(tags_str)
    for tags in tags_list:
        if tags == args:
            tags_list.remove(args)
            user.tags = json.dumps(tags_list, ensure_ascii=False)
            user_session.commit()
            await unsubscribes.finish("取消订阅成功！")
    await unsubscribes.finish("您没有订阅这个 Tag！")


@list_subscribes.handle()
async def list_sub_handle(target: Target = Depends(get_target)):
    id_ = f"{'private' if target.private else 'group'}_{target.id}"
    user = user_session.query(User).filter_by(id=id_).first()
    if user is None:
        await list_subscribes.finish("您还没有订阅任何 Tag！")
    tags_str = user.tags
    tags_list: List[List[str]] = json.loads(tags_str)
    msg = "您订阅的 Tag 有：\n"
    for index, tags in enumerate(tags_list):
        msg += f"{index + 1}. {' '.join(tags)}\n"
    await list_subscribes.finish(msg)


@test.handle()
async def test_handle():
    await test.send("开始测试下载！")

    tags = ["桜都字幕组", "GILRS", "BAND", "CRY"]

    torrent_data = await fetch_torrent_data(
        f"{plugin_config.acgrip_url}/t/302631.torrent"
    )
    torrent_info = await torrent_downloader.download_torrent(
        torrent_data, generate_folder_name(tags)
    )
    task_manager.add(
        {
            "id": "private_2667292003",
            "content": torrent_info,
            "torrent_id": 302631,
        }
    )
