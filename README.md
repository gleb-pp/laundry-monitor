# Laundry Monitor

[![CI](https://github.com/gleb-pp/laundry-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)
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

-- 

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


## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/gleb-pp/laundry-monitor.git
cd laundry-monitor
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Run the application

```bash
poetry run uvicorn src.main:app --reload
```

Then open:

```bash
http://127.0.0.1:8000/docs
```