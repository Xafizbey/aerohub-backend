# AeroHub Backend

Production-ready FastAPI backend for the **AeroHub In-Flight Entertainment System**.  
Designed to operate fully offline on an airplane's internal WiFi network.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Server | Uvicorn |
| Containers | Docker + Docker Compose |
| Reverse Proxy | Nginx (config included) |

---

## Project Structure

```
aerohub-backend/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py          # register, login, /me
│   │   │   ├── movies.py        # CRUD + poster/HLS upload
│   │   │   ├── music.py         # CRUD + playlists + audio upload
│   │   │   └── analytics.py     # track views/plays, top-10 stats
│   │   └── router.py
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── security.py          # JWT + bcrypt helpers
│   │   └── logging.py           # Structured logging setup
│   ├── db/
│   │   ├── base.py              # DeclarativeBase
│   │   └── session.py           # Async engine + get_db dependency
│   ├── middleware/
│   │   └── logging.py           # Request/response logging middleware
│   ├── models/
│   │   ├── user.py              # User, UserRole
│   │   ├── movie.py             # Movie, MovieCategory
│   │   ├── music.py             # Music, Playlist, PlaylistTrack
│   │   └── analytics.py        # ViewHistory, PlayHistory
│   ├── schemas/
│   │   ├── user.py, movie.py, music.py, analytics.py, common.py
│   ├── services/
│   │   ├── auth.py              # register/login/get_current_user
│   │   ├── movie.py             # movie business logic
│   │   ├── music.py             # music + playlist logic
│   │   ├── analytics.py         # tracking + aggregations
│   │   └── media.py             # file upload handler
│   ├── utils/
│   │   └── exceptions.py        # Global exception handlers
│   └── main.py                  # FastAPI app + lifespan
├── alembic/                     # DB migrations
├── scripts/
│   ├── seed.py                  # Demo data seeder
│   └── create_admin.py          # Admin user helper
├── nginx/aerohub.conf           # Production nginx config
├── media/                       # Local media storage (offline)
├── logs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Quick Start (Docker)

```bash
# 1. Clone / enter the backend directory
cd aerohub-backend

# 2. Create environment file
cp .env.example .env
# Edit SECRET_KEY in .env !

# 3. Start services (API + PostgreSQL)
docker-compose up --build

# 4. Run migrations (first time)
docker-compose exec api alembic upgrade head

# 5. Seed demo data
docker-compose exec api python scripts/seed.py
```

API is now at **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**

---

## Local Development (without Docker)

```bash
# Prerequisites: Python 3.12, PostgreSQL running locally

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Set DATABASE_URL to your local PostgreSQL instance

# Run migrations
alembic upgrade head

# Seed
python scripts/seed.py

# Start dev server with hot reload
uvicorn app.main:app --reload --port 8000
```

---

## API Overview

### Authentication
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new passenger |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Current user profile |
| PATCH | `/api/v1/auth/me` | Update profile |

### Movies
| Method | Path | Auth |
|---|---|---|
| GET | `/api/v1/movies` | Passenger |
| POST | `/api/v1/movies` | Admin |
| GET | `/api/v1/movies/{id}` | Passenger |
| PATCH | `/api/v1/movies/{id}` | Admin |
| DELETE | `/api/v1/movies/{id}` | Admin |
| POST | `/api/v1/movies/{id}/poster` | Admin (file upload) |
| POST | `/api/v1/movies/{id}/hls` | Admin (set .m3u8 path) |
| GET | `/api/v1/movies/categories` | Passenger |
| POST | `/api/v1/movies/categories` | Admin |

### Music
| Method | Path | Auth |
|---|---|---|
| GET | `/api/v1/music` | Passenger |
| POST | `/api/v1/music` | Admin |
| GET | `/api/v1/music/{id}` | Passenger |
| PATCH | `/api/v1/music/{id}` | Admin |
| DELETE | `/api/v1/music/{id}` | Admin |
| POST | `/api/v1/music/{id}/audio` | Admin (file upload) |
| POST | `/api/v1/music/{id}/cover` | Admin (file upload) |

### Playlists
| Method | Path | Auth |
|---|---|---|
| GET | `/api/v1/music/playlists/me` | Passenger |
| POST | `/api/v1/music/playlists` | Passenger |
| GET/PATCH/DELETE | `/api/v1/music/playlists/{id}` | Owner |
| POST | `/api/v1/music/playlists/{id}/tracks` | Owner |
| DELETE | `/api/v1/music/playlists/{id}/tracks/{tid}` | Owner |

### Analytics
| Method | Path | Auth |
|---|---|---|
| POST | `/api/v1/analytics/views` | Passenger |
| POST | `/api/v1/analytics/plays` | Passenger |
| GET | `/api/v1/analytics/movies/top` | Admin |
| GET | `/api/v1/analytics/music/top` | Admin |

---

## Roles

| Role | Capabilities |
|---|---|
| `passenger` | Browse & stream content, manage own playlists, track progress |
| `admin` | Full CRUD on all content, upload media, view analytics |

Default registration creates `passenger` role. Use `scripts/create_admin.py` to promote.

---

## HLS Video Support

The backend stores `.m3u8` playlist paths for HLS streams (pre-encoded video segments stored locally on the airplane server). Set the path via:

```
POST /api/v1/movies/{id}/hls
Body: hls_path=/media/videos/movie_name/index.m3u8
```

Nginx serves the segments directly with proper MIME types for maximum throughput.

---

## Offline / Airplane WiFi Design

- All media is stored locally under `media/` — no internet required
- JWT tokens have a 24-hour expiry (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- CORS can be locked to the airplane subnet via `CORS_ORIGINS`
- Static files are served by Nginx directly (bypasses FastAPI for performance)
- No external CDN or third-party service dependencies

---

## Demo Credentials (after seed)

| Role | Email | Password |
|---|---|---|
| Admin | admin@aerohub.kz | Admin1234! |
| Passenger | passenger@aerohub.kz | Pass1234! |
