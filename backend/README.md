# Backend Service (FastAPI)

This folder contains the FastAPI + SQLAlchemy backend for the Legacy Skye Steward handover & analytics platform. The default database is SQLite so you can run everything locally without additional services.

## Quick Start

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python .\scripts\seed_demo.py
python -m uvicorn app.main:app --reload --app-dir .
```

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python ./scripts/seed_demo.py
python -m uvicorn app.main:app --reload --app-dir .
```

Once the server is running visit http://127.0.0.1:8000/docs for the interactive API documentation or hit the `/health` endpoint to verify.

## Testing

Activate your virtual environment and run:

```bash
cd backend
pytest
```

## Troubleshooting

- **SQLite file locks**: Stop the server, delete `app.db`, then rerun `alembic upgrade head` to recreate the schema.
- **Import error for `DATABASE_URL`**: All configuration lives in `app.config`. Import database objects from `app.db` instead.
- **HTTP 422 on POST**: Ensure dates are ISO8601 (e.g. `2024-01-01T08:00:00Z`) and that the JSON body is valid.

## Extra Tools

- `scripts/seed_demo.py` inserts demo handovers and guest notes using timezone-aware UTC datetimes. Run it whenever you need fresh sample data.
- `tests/local.http` provides quick REST Client snippets for manual testing inside VS Code.
