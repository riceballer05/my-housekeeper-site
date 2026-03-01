from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import pages, api

app = FastAPI(title="お片付け専門ハウスキーパーサービス API", description="整理収納サービスのバックエンド")

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# ルーターの登録
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
