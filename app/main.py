from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.logging import RequestLoggingMiddleware
from app.utils.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    (settings.MEDIA_ROOT / "posters").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "videos").mkdir(exist_ok=True)
    (settings.MEDIA_ROOT / "music").mkdir(exist_ok=True)
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
    lifespan=lifespan,
)

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


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
