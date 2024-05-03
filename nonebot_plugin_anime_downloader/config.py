from pydantic import BaseModel


class Config(BaseModel):
    anime_url: str = "http://127.0.0.1"
    """你的服务器公网地址，用于提供视频观看链接"""
    acgrip_url: str = "https://acgrip.art"
    """ACG.RIP 的 URL"""
    acgrip_interval: int = 600
    """从 ACG.RIP 获取种子数据的时间间隔（秒）"""
    qbittorrent_host: str = "localhost:8080"
    """qBittorrent WebUI 的地址"""
    qbittorrent_username: str = "admin"
    """qBittorrent WebUI 的用户名"""
    qbittorrent_password: str = "adminadmin"
    """qBittorrent WebUI 的密码"""
    download_path: str = "/downloads"
    """种子下载到的路径"""
