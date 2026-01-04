from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .routers import note, provider, model, config, rag, rag_history


class UTF8JSONResponse(JSONResponse):
    def __init__(self, content, status_code=200, headers=None, media_type=None, background=None):
        super().__init__(
            content,
            status_code=status_code,
            headers=headers,
            media_type=media_type or "application/json; charset=utf-8",
            background=background,
        )


def create_app(lifespan) -> FastAPI:
    app = FastAPI(title="BiliNote", lifespan=lifespan, default_response_class=UTF8JSONResponse)
    app.include_router(note.router, prefix="/api")
    app.include_router(provider.router, prefix="/api")
    app.include_router(model.router,prefix="/api")
    app.include_router(config.router,  prefix="/api")
    app.include_router(rag.router, prefix="/api")
    app.include_router(rag_history.router, prefix="/api")

    return app
