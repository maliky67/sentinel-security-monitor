# Sentinel — Security Event Detection Platform

A Python-based security event monitoring and threat detection
platform, built to demonstrate backend engineering and
cybersecurity practices.

## Project Status

Week 1 — Foundation development

## Planned Features

- CSV and JSONL security log ingestion
- Event validation and normalization
- Rule-based threat detection
- SQLite event and alert persistence
- REST API with FastAPI
- Interactive analytics dashboard
- Automated testing and security checks

## Technology Stack

- Python 3.13
- Pydantic
- Pytest
- Ruff
- SQLite, SQLAlchemy, FastAPI (planned)
- Streamlit (planned)

## Getting Started

### Requirements

- Python 3.13
- Git

### Install on Windows

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

### Run Tests

```powershell
python -m pytest -v
```

### Check Code Quality

```powershell
ruff check .
ruff format --check .
```

## Project Structure

- `src/sentinel/`: Application source code
- `tests/`: Automated tests
- `docs/`: Engineering documentation

## Security

Use synthetic or explicitly authorized log data only.
Do not commit credentials or sensitive production logs.

## Roadmap

1. Event validation
2. Log ingestion
3. Detection engine
4. SQLite persistence
5. REST API
6. Dashboard
7. Security hardening and release

## License

MIT
