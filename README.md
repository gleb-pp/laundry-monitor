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

- `free` — the machine was explicitly reported as available
- `busy` — the machine was reported as currently in use
- `probably_free` — the machine was previously reported as busy, but the expected busy period has likely ended and no newer report has confirmed the current state yet
- `unavailable` — the machine is temporarily unavailable for use, for example due to maintenance or a malfunction

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
- `machine_id: int` — machine identifier
- `status: free | busy | unavailable` — reported machine status
- `time_remaining: int | null` — optional remaining time in minutes; use `null` when the machine is `free` or `unavailable`

**Example request**
```bash
curl -X POST "http://127.0.0.1:8000/report?machine_id=1&status=busy&time_remaining=25"
```

**Example response**
```json
{
  "success": true
}
```

### `GET /machines`
Return all machines with inferred current status.

**Example response**
```json
[
  {
    "id": 1,
    "dormitory": 1,
    "name": "Washer 1",
    "type": "washing",
    "status": "free"
  },
  {
    "id": 2,
    "dormitory": 1,
    "name": "Dryer 1",
    "type": "drying",
    "status": "free"
  }
]
```

### `GET /machines/{machine_id}/history`
Return recent reports for a specific machine.

**Example response**
```json
[
  {
    "id": 1,
    "machine_id": 2,
    "status": "free",
    "timestamp": "2026-04-03T16:19:29.062Z",
    "time_remaining": null
  }
]
```

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

### 2. Install poetry

```bash
pip install poetry
```

### 3. Install project dependencies

```bash
poetry install
```

### 4. Run the application

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

| ID | Dormitory | Name      | Type    |
|----|-----------|-----------|---------|
| 1  | 1         | Washer 1  | Washing |
| 2  | 1         | Dryer 1   | Drying  |
| 3  | 2         | Washer 2  | Washing |
| 4  | 2         | Dryer 2   | Drying  |

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
- **Cyclomatic complexity:** maximum McCabe complexity per function is 7
- **Style:** no flake8 errors
- **Security:** no high-severity Bandit findings
