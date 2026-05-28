from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.admin import create_admin, _load_logo_from_db
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.services.websocket import order_ws
from app.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    (settings.MEDIA_ROOT / "posters").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "videos").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "music").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "cafe").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "logos").mkdir(exist_ok=True)
    # Ensure the singleton company settings row exists
    from app.db.session import AsyncSessionLocal
    from app.services.company import get_or_create_settings
    async with AsyncSessionLocal() as session:
        await get_or_create_settings(session)
        await session.commit()
    # Apply saved logo to the sqladmin sidebar
    await _load_logo_from_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AeroHub — In-Flight Entertainment System API. "
        "Designed for offline operation on airplane WiFi networks."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path=settings.ROOT_PATH,
    lifespan=lifespan,
)

# ── Admin panel ───────────────────────────────────────────────────────────────
create_admin(app)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = ["*"] if settings.CORS_ALLOW_ALL else settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request logging ───────────────────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# ── Static media (served locally — no CDN in airplane) ───────────────────────
app.mount("/media", StaticFiles(directory=str(settings.MEDIA_ROOT)), name="media")

# ── Static assets (favicon, etc.) ────────────────────────────────────────────
from pathlib import Path as _Path
app.mount("/static", StaticFiles(directory=str(_Path(__file__).parent.parent / "static")), name="static")


@app.websocket("/ws/orders")
async def ws_orders(websocket: WebSocket):
    await order_ws.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive ping/pong
    except WebSocketDisconnect:
        order_ws.disconnect(websocket)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
