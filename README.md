# Speed Reading App

Flask web app for speed-reading practice with PostgreSQL (Docker) and Alembic migrations.

## 1) Quick Start (Windows PowerShell)

Run these commands from project root:

```powershell
docker compose up -d postgres
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\flask.exe --app app db upgrade
.\.venv\Scripts\python.exe scripts\seed_demo.py
.\.venv\Scripts\python.exe app.py
```

App URL: `http://127.0.0.1:5000`

## 2) Demo Accounts

- Admin: `admin_demo` / `Admin@123`
- User: `demo_user` / `Demo@123`
- User: `demo_reader` / `Reader@123`

## 3) Database

- DB engine: PostgreSQL 16 (Docker)
- Host: `127.0.0.1`
- Port: `5432`
- Database: `speed_reading`
- User: `speed_user`
- Password: `speed_pass`
- Docker volume: `speed_reading_postgres_data`

The app reads DB connection from `.env` (`DATABASE_URL`).

## 4) Seed Demo Data

Seed script is idempotent for demo users (safe to run many times):

```powershell
.\.venv\Scripts\python.exe scripts\seed_demo.py
```

What it creates:

- 1 admin account + 2 user accounts
- Sample documents
- Sample reading sessions

## 5) Backup / Restore

Create SQL backup:

```powershell
docker exec speed_reading_postgres pg_dump -U speed_user -d speed_reading > data\backup_speed_reading.sql
```

Restore from SQL backup:

```powershell
Get-Content data\backup_speed_reading.sql | docker exec -i speed_reading_postgres psql -U speed_user -d speed_reading
```

## 6) Environment Notes

- Commit `.env.example`, do not commit `.env`.
- If `5432` is busy, change port mapping in `docker-compose.yml`.
- Migration files are in `migrations/versions/`.
