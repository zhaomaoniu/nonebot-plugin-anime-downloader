from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

# 将静态文件夹设置为存放视频文件的目录
app.mount("/acgrip", StaticFiles(directory="acgrip"), name="acgrip")


@app.get("/")
async def index():
    # 在主页上返回一个HTML页面，其中包含一个视频元素
    return HTMLResponse("""
        <html>
            <head>
                <title>视频播放</title>
            </head>
            <body>
                <h1>视频播放</h1>
                <video width="640" height="480" controls>
                    <source src="/acgrip/[Nekomoe kissaten][Nijiyon Animation S2][03][1080p][JPSC].mp4" type="video/mp4">
                </video>
            </body>
        </html>
    """)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)