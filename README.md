# Nonebot-Plugin-Anime-Downloader
✨ 基于 qBittorrent Web UI 的番剧下载 NoneBot 插件 ✨

## 介绍
为了解决每周手动下载番剧的痛苦，本插件基于 qBittorrent Web UI 开发，通过轮番爬取 ACG.RIP，实现番剧下载及提醒的自动化

> 使用了 [NoneBot-Plugin-Alconna](https://github.com/nonebot/plugin-alconna) 实现了跨平台哦

## 功能
- [x] 番剧订阅
- [x] 番剧下载
- [x] 番剧提醒

## 使用
| 命令 | 别名 | 说明 | 示例 |
| --- | --- | --- | --- |
| sub | 订阅 | 通过 Tag 订阅番剧 | `sub Up to 21°C Nijiyon Animation 2 MP4` |
| unsub | 取消订阅 | 通过 Tag 取消订阅番剧 | `unsub Up to 21°C Nijiyon Animation 2 MP4` |
| listsub | sublist, 订阅列表 | 查看当前用户/群组的订阅列表 | `sublist` |
| amnsc | 番剧搜索, 搜索番剧, animesearch | 通过关键词搜索番剧 | `amnsc Nijiyon Animation 2` |
| amnd | 番剧下载, 下载番剧, animedownload | 通过 资源ID 下载番剧 | `amnd 114514` |

这里的 Tag 就是用来在 ACG.RIP 搜索的关键词，番剧名、分辨率、字幕组等等，只要能在 ACG.RIP 搜索到的都可以

> 记得加上你的命令头哦

## 效果

**user**: `/sub Up to 21°C Nijiyon Animation 2 MP4`

**bot**: 订阅成功！

**user**: `/sublist`

**bot**: 您订阅的 Tag 有：
1. Up to 21°C Nijiyon Animation 2 MP4

(过了一段时间)

**bot**: [Up to 21°C] Love Live！虹咲學園 學園偶像同好會 短篇動畫 第二季 / Nijiyon Animation 2 - 04 (ABEMA 1920x1080 AVC AAC MP4) 现在可以观看了！
[http://example.com/anime/302322](http://example.com/anime/302322)

**user**: `/amnd 302322`

**bot**: [Up to 21°C] Love Live！虹咲學園 學園偶像同好會 短篇動畫 第二季 / Nijiyon Animation 2 - 04 (ABEMA 1920x1080 AVC AAC MP4) 现在可以观看了！
[http://example.com/anime/302322](http://example.com/anime/302322)


## 安装方法
<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-anime-downloader

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-anime-downloader
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-anime-downloader
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-anime-downloader
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-anime-downloader
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_steam_info"]

</details>


## 配置
| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `ANIME_URL` | `http://127.0.0.1` | 你的服务器公网地址，用于提供视频观看链接 |
| `ACGRIP_URL` | `https://acgrip.art` | ACG.RIP 的 URL |
| `ACGRIP_INTERVAL` | `600` | 爬取 ACG.RIP 的间隔时间（秒），时间越短，提醒越及时，但是会增加服务器压力 |
| `QBITTORRENT_HOST` | `localhost:8080` | qBittorrent Web UI 的地址 |
| `QBITTORRENT_USERNAME` | `admin` | qBittorrent Web UI 的用户名 |
| `QBITTORRENT_PASSWORD` | `adminadmin` | qBittorrent Web UI 的密码 |
| `DOWNLOAD_PATH` | `/downloads` | 种子下载到的路径 |

### 注意
- 安装 qBittorrent 并启用 Web UI
- NoneBot 的 Driver(驱动器) 需要包含 `FastAPI`
- NoneBot 和 qBittorrent 需要在同一台服务器上

关于 ACG.RIP 的访问性问题：
1. 默认使用的 acgrip.art 域名可以在国内访问，但貌似国外访问不了
2. 如果你的服务器在国外，可以使用 acg.rip 域名
3. 环大陆用哪个都可以

## 常见问题
- 在 Satori 适配器下，NoneBot-Plugin-Alconna 在 0.45.2 及以前对群聊/私聊的判断有误，导致无法正常使用，建议升级到 0.45.2 以上版本

## 鸣谢
- [NoneBot-Plugin-Alconna](https://github.com/nonebot/plugin-alconna) 提供了跨平台的支持
- [kumoSleeping](https://github.com/kumoSleeping) 不自己下番的懒猪
