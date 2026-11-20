# Payment Gateway Project

A Python-based Payment Gateway application demonstrating payment processing, retry handling, gateway fallback mechanisms, structured logging, database persistence, and automated testing.

## Features

- **Payment Processing:** Validates payment details and processes payments through configured gateways.
- **Retry Mechanism:** Supports configurable retries with exponential backoff and jitter.
- **Gateway Fallback:** Uses a fallback gateway when the primary gateway is unavailable or fails.
- **Custom Exceptions:** Handles payment failures, gateway errors, and timeouts.
- **Audit Logging:** Records payment-related events for tracking and debugging.
- **Database Integration:** Uses SQLAlchemy to store payment records and payment attempt history.
- **Database Migrations:** Uses Alembic to manage database schema changes.
- **Automated Testing:** Uses pytest for unit tests, mocking, and database testing.
- **Code Quality:** Uses Ruff for linting and formatting.
- **Pre-commit Hooks:** Runs Ruff checks automatically before Git commits.
- **CI Pipeline:** Uses GitHub Actions to automate code quality checks and tests.

## Tech Stack

- Python 3.12
- SQLAlchemy
- Alembic
- Pytest
- Pytest-Cov
- Ruff
- Pre-commit
- GitHub Actions
- SQLite

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/anushka-DT/PaymentGatewayProject.git
cd PaymentGatewayProject
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

Install application dependencies and development tools:

```bash
pip install -r requirements-dev.txt
```

## Database Setup

Apply the database migrations:

```bash
alembic upgrade head
```

To check the current migration revision:

```bash
alembic current
```

To view available migration history:

```bash
alembic history
```

## Running Tests

Run the complete test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=payment_gateway --cov-report=term-missing
```

Run a specific test file:

```bash
pytest tests/test_client.py -v
```

## Code Quality Checks

Run Ruff linting:

```bash
ruff check .
```

Check code formatting:

```bash
ruff format --check .
```

Automatically format Python files:

```bash
ruff format .
```

## Pre-commit Setup

Install the Git pre-commit hook:

```bash
pre-commit install
```

Run all configured hooks manually:

```bash
pre-commit run --all-files
```

Once installed, Ruff checks run automatically before each Git commit.

## Database Migration Commands

Create a new migration:

```bash
alembic revision --autogenerate -m "describe migration"
```

Apply migrations:

```bash
alembic upgrade head
```

Roll back one migration:

```bash
alembic downgrade -1
```

## CI/CD

GitHub Actions is configured to run automated checks on pushes and pull requests.

The workflow includes:

- Ruff linting.
- Ruff formatting validation.
- Pytest execution with coverage.

## Project Goals

This project was developed to practice Python application development concepts, including object-oriented programming, exception handling, decorators, retry mechanisms, logging, database operations, migrations, automated testing, Git workflows, and CI/CD.
