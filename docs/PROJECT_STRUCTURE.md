# Project Structure

```
speed_reading/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .env
|-- .env.example
|-- docker-compose.yml
|-- backend/
|   |-- __init__.py
|   |-- server.py
|   |-- requirements.txt
|   |-- config/
|   |   |-- __init__.py
|   |   |-- database.py
|   |   `-- settings.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- user.py
|   |   |-- document.py
|   |   `-- reading_session.py
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- main.py
|   |   |-- auth.py
|   |   |-- user.py
|   |   |-- reading.py
|   |   `-- admin.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- file_handler.py
|   |   |-- text_processor.py
|   |   `-- stats_calculator.py
|   `-- utils/
|       |-- __init__.py
|       |-- decorators.py
|       |-- validators.py
|       `-- timezone.py
|-- frontend/
|   |-- templates/
|   `-- static/
|-- data/
|   |-- instance/
|   `-- uploads/
|-- migrations/
|   |-- env.py
|   `-- versions/
|-- scripts/
|   `-- seed_demo.py
`-- docs/
    |-- PROJECT_STRUCTURE.md
    `-- POSTGRES_SETUP.md
```

Run from project root:

```powershell
.\.venv\Scripts\python.exe app.py
```

Apply migration:

```powershell
.\.venv\Scripts\flask.exe --app app db upgrade
```

Seed demo data:

```powershell
.\.venv\Scripts\python.exe scripts\seed_demo.py
```
