# Laundry Monitor

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](#)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)](#)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)](#)
[![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?logo=pydantic&logoColor=white)](#)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-60A5FA?logo=poetry&logoColor=white)](#)
[![Pytest](https://img.shields.io/badge/Pytest-Tests-0A9EDC?logo=pytest&logoColor=white)](#)
[![Coverage](https://img.shields.io/badge/Coverage-%3E%3D70%25-brightgreen)](#)
[![Bandit](https://img.shields.io/badge/Bandit-Security-F59E0B)](#)

A simple web application where dormitory students can report and view the real‑time status of washing and drying machines, reducing unnecessary trips to the laundry room.

This project is part of the Software Quality and Reliability course at Innopolis University. The main focus is on implementing autonomous quality gates, testing and analysis techniques, and studying CI/CD practices.

---

## Features

- report machine status via API
- view all machines with inferred status
- inspect machine report history
- preloaded machine seed data on startup
- SQLite-based local persistence
- automated testing and quality gates

### Inferred machine states

The system supports the following effective states:

- `free`
- `busy`
- `probably_free`
- `unavailable`

Status is inferred using report timestamp and optional `time_remaining`.

---

## Tech Stack

- **Language:** Python 3.12
- **Backend:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Validation / Schemas:** Pydantic
- **Dependency management:** Poetry
- **Testing:** pytest, pytest-cov
- **Code quality:** flake8, radon, bandit
- **CI/CD:** GitHub Actions

---

## API

### `POST /report`
Submit a machine status report.

**Parameters**
- `machine_id: int`
- `status: free | busy | unavailable`
- `time_remaining: int | null`

### `GET /machines`
Return all machines with inferred current status.

### `GET /machines/{id}/history`
Return recent reports for a specific machine.

### OpenAPI docs
Swagger UI is available at:

```bash
http://127.0.0.1:8000/docs
```

---

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/gleb-pp/laundry-monitor.git
cd laundry-monitor
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install poetry

```bash
pip install poetry
```

### 4. Install project dependencies

```bash
poetry install
```

### 5. Run the application

```bash
poetry run uvicorn src.main:app --reload
```

Then open:

```bash
http://127.0.0.1:8000/docs
```

---

## Seed Data

On startup, the application creates database tables and preloads several machines if the database is empty.

Default initial data:
- Washer 1
- Dryer 1
- Washer 2
- Dryer 2

---

## Testing

Run all tests:

```bash
poetry run pytest -q
```

Run tests with coverage:

```bash
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

---

## Quality Gates

Run style, complexity, security, and test checks from the project root:

```bash
poetry run flake8 src tests
poetry run radon cc src -a -s
poetry run radon mi src -s
poetry run bandit -r src -lll
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

Target thresholds:

- **Unit tests:** 100% passing
- **Coverage:** at least 70%
- **Cyclomatic complexity:** below threshold
- **Style:** no flake8 errors
- **Security:** no high-severity Bandit findings
