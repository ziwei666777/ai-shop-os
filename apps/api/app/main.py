from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.interfaces.http.routes import router
from apps.api.app.interfaces.http.commerce_routes import router as commerce_router


def create_app() -> FastAPI:
    """创建 FastAPI 应用，所有业务入口都通过 HTTP 路由进入应用层。"""
    app = FastAPI(title="AI Shop OS API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.include_router(commerce_router)
    return app


app = create_app()
