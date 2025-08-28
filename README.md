# DY Crane Safety Management API

This project is the backend API for the DY Crane Safety Management System. It provides a RESTful API for managing construction sites, cranes, drivers, and safety documents.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.8+
*   PowerShell 7+ (for Windows) or a bash-compatible shell (for Linux/macOS)
*   PostgreSQL 13+
*   `psql` command-line client (optional, but recommended)

### Installation

1.  **Clone the repository**
    ```sh
    git clone <repository-url>
    cd dycrane_backend_proto
    ```

2.  **Create a `.env` file**
    Copy the `.env.example` file to a new file named `.env` and update the database connection details.
    ```sh
    cp .env.example .env
    ```

3.  **Set up the database**
    Make sure you have a running PostgreSQL instance and that the user specified in your `.env` file has permission to create databases.

4.  **Run the database setup script**
    This will create the database, tables, and seed it with initial data.
    ```sh
    ./scripts/dev.sh db
    ```

## Usage

The `scripts/dev.sh` script is the main entry point for development tasks.

*   **Initialize the database:**
    ```sh
    ./scripts/dev.sh db
    ```

*   **Run the E2E tests:**
    ```sh
    ./scripts/dev.sh test
    ```

*   **Run the E2E tests with verbose output:**
    ```sh
    ./scripts/dev.sh test/verbose
    ```

*   **Run the API server:**
    To run the server, you can use `uvicorn` directly.
    ```sh
    uvicorn server.main:app --reload
    ```

## Project Structure

The project is organized into a layered architecture:

```
repo-root/
├─ server/
│  ├─ __init__.py
│  ├─ main.py                # FastAPI app creation and entry point
│  ├─ config.py              # Pydantic settings configuration
│  ├─ database.py            # Database session management
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ routes.py            # Main API router
│  │  └─ routers/             # Resource-specific routers
│  │     ├─ sites.py
│  │     ├─ cranes.py
│  │     ├─ assignments.py
│  │     └─ documents.py
│  ├─ domain/
│  │  ├─ __init__.py
│  │  ├─ models.py            # SQLAlchemy ORM models
│  │  ├─ schemas.py           # Pydantic schemas
│  │  ├─ repositories.py      # Data access layer
│  │  └─ services.py          # Business logic layer
│  └─ ...
├─ tests/
│  └─ e2e/                   # End-to-end tests
│     ├─ client.py
│     ├─ fixtures.py
│     ├─ validators.py
│     ├─ test_healthcheck.py
│     └─ test_workflow.py
├─ scripts/
│  ├─ dev.sh                 # Main development script (for bash)
│  ├─ dev.ps1                # Original PowerShell script
│  └─ db_runner.py           # Python fallback for DB operations
├─ sql/                       # SQL scripts for DB setup
│  ├─ init_db.sql
│  ├─ init_view.sql
│  ├─ truncate.sql
│  └─ seed.sql
├─ .env.example               # Example environment variables
├─ .gitignore
├─ requirements.txt
└─ README.md
```