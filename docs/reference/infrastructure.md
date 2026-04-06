# Infrastructure & Development Environment

## Docker Compose Services

```
┌─────────────────────────────────────────────────┐
│                  docker-compose                  │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ backend  │  │ postgres │  │  redis   │      │
│  │ :8000    │→ │ :5432    │  │ :6379    │      │
│  │ FastAPI  │  │ PG 16    │  │ Redis 7  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│       ↑                                          │
│   host:8000                                      │
└─────────────────────────────────────────────────┘
```

### Services

| Service | Image | Port (host:container) | Purpose |
|---|---|---|---|
| **backend** | Built from `Dockerfile` | 8000:8000 | FastAPI app + Uvicorn |
| **postgres** | postgres:16-alpine | 5432:5432 | Primary database |
| **redis** | redis:7-alpine | 6379:6379 | Caching, rate limiting, future job queue |

### Volumes

| Volume | Mounted to | Purpose |
|---|---|---|
| `postgres_data` | postgres:/var/lib/postgresql/data | Persist database across restarts |
| `redis_data` | redis:/data | Persist Redis cache |

### Environment Variables

Backend reads from `.env` file:

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | Yes | postgres | Database user |
| `POSTGRES_PASSWORD` | Yes | postgres | Database password |
| `POSTGRES_DB` | Yes | app_db | Database name |
| `POSTGRES_SERVER` | No | postgres | Hostname (use `postgres` in Docker, `localhost` for local dev) |
| `POSTGRES_PORT` | No | 5432 | Database port |
| `SECRET_KEY` | Yes | — | JWT signing key |
| `REDIS_HOST` | No | redis | Redis hostname |
| `REDIS_PORT` | No | 6379 | Redis port |

### Docker Compose Profiles

Default `docker-compose up` starts all services. Future profiles:

| Profile | Services | Use case |
|---|---|---|
| (default) | backend, postgres, redis | Full development stack |
| `db-only` | postgres, redis | Local dev — run backend outside Docker |

### Networking

All services share the default Docker network. Backend connects to postgres via hostname `postgres` and redis via hostname `redis`. For local development outside Docker, use `localhost` with exposed ports.

### Health Checks

| Service | Check | Interval |
|---|---|---|
| postgres | `pg_isready -U $POSTGRES_USER` | 5s |
| redis | `redis-cli ping` | 5s |
| backend | `GET /health` | 10s |

Backend waits for postgres and redis to be healthy before starting (`depends_on` with `condition: service_healthy`).

## Makefile Commands

### Quick Reference

```
make help          — show all available commands
make up            — start all services
make down          — stop all services
make restart       — restart all services
make logs          — tail all logs
make logs-backend  — tail backend logs only

make migrate       — run pending migrations (alembic upgrade head)
make migrate-create — create new migration (alembic revision --autogenerate)
make migrate-down  — rollback last migration (alembic downgrade -1)
make migrate-history — show migration history

make test          — run all tests
make test-cov      — run tests with coverage report
make lint          — run ruff check + format
make format        — auto-format with ruff

make shell         — open bash in backend container
make db-shell      — open psql in postgres container
make db-reset      — drop and recreate database (destructive!)

make install       — install Python dependencies locally
make seed          — run seed script (initial data)
```

### Command Grouping

| Group | Commands | When to use |
|---|---|---|
| **Docker** | up, down, restart, logs, shell | Managing the dev stack |
| **Database** | migrate, migrate-create, migrate-down, db-shell, db-reset | Schema changes |
| **Testing** | test, test-cov | Before commits and PRs |
| **Code quality** | lint, format | Before commits (also runs in pre-commit) |
| **Setup** | install, seed | First-time setup |

### Migration Workflow

When adding a new feature with database tables:

1. Define the table in `docs/reference/erd.md` (doc first)
2. Write the SQLAlchemy model in `app/features/{name}/models.py`
3. Import the model in `app/main.py` (so Alembic discovers it)
4. Run `make migrate-create msg="add {table_name}"` — generates migration file
5. Review the generated migration in `alembic/versions/`
6. Run `make migrate` — applies the migration
7. If something went wrong: `make migrate-down` — rolls back one step

### Local Development (without Docker)

For running backend locally against Dockerized services:

```bash
# Start only database + redis
docker-compose up postgres redis -d

# Set local env
export POSTGRES_SERVER=localhost
export REDIS_HOST=localhost

# Install and run
make install
make migrate
uvicorn app.main:app --reload --port 8000
```

## .env File Template

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db
POSTGRES_SERVER=postgres
POSTGRES_PORT=5432

# Security
SECRET_KEY=change-me-in-production

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# App
DEBUG=true
LOG_LEVEL=INFO
```

Copy to `.env` and adjust for your environment. Never commit `.env` — use `.env.sample` as the template.
