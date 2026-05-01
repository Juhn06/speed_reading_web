# PostgreSQL Setup (Recommended)

## 1) Prepare environment

Copy `.env.example` to `.env` and keep the PostgreSQL `DATABASE_URL` value.

```powershell
Copy-Item .env.example .env
```

## 2) Start PostgreSQL with Docker

```powershell
docker compose up -d postgres
docker compose ps
```

Default DB config from `docker-compose.yml`:

- Host: `127.0.0.1`
- Port: `5432`
- Database: `speed_reading`
- User: `speed_user`
- Password: `speed_pass`

## 3) Install Python dependencies

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

## 4) Apply migration

Current repository already includes an initial migration. Apply it:

```powershell
.\.venv\Scripts\flask.exe --app app db upgrade
```

For later schema changes, create and apply a new migration:

```powershell
.\.venv\Scripts\flask.exe --app app db migrate -m "describe change"
.\.venv\Scripts\flask.exe --app app db upgrade
```

## 5) Run application

```powershell
.\.venv\Scripts\python.exe app.py
```

## 6) Seed demo data (recommended for presentations)

```powershell
.\.venv\Scripts\python.exe scripts\seed_demo.py
```

Demo accounts:

- Admin: `admin_demo` / `Admin@123`
- User: `demo_user` / `Demo@123`
- User: `demo_reader` / `Reader@123`

## 7) Export database backup

```powershell
docker exec speed_reading_postgres pg_dump -U speed_user -d speed_reading > data\backup_speed_reading.sql
```
