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
    git clone https://github.com/viakisun/dycrane_backend_proto
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

### Development Scripts

The development scripts are the main entry point for development tasks.

**For Windows (PowerShell):**
```powershell
# Initialize the database
./scripts/dev.ps1 -Command db

# Run all tests
./scripts/dev.ps1 -Command test

# Run all tests with verbose output
./scripts/dev.ps1 -Command test/verbose
```

**For Linux/macOS (Bash):**
```sh
# Initialize the database
./scripts/dev.sh db

# Run all tests
./scripts/dev.sh test

# Run all tests with verbose output
./scripts/dev.sh test/verbose
```

### Running the API Server
To run the API server directly for development, use `uvicorn`:
```sh
uvicorn server.main:app --reload
```

### Running the Frontend Test Client
The `client` directory contains a TypeScript-based React application to visually test the API workflow.

1.  **Navigate to the client directory:**
    ```sh
    cd client
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Run the client:**
    ```sh
    npm run dev
    ```
    This will start the client on `http://localhost:3000`. The client will proxy API requests to the backend server running on port 8000.

## Testing

This project includes both End-to-End (E2E) and unit tests to ensure the quality and correctness of the application.

### Test Suites

*   **End-to-End (E2E) Tests (`tests/e2e`):** These tests simulate the full user workflow from a client's perspective, making real HTTP requests to the API.
    *   `test_workflow.py`: This test covers the 9-step business workflow. **Note:** This test is currently partially implemented and will be completed as the backend services are refactored.
    *   `test_healthcheck.py`: A simple test to check if the API is running and connected to the database.

*   **Unit Tests (`tests/unit`):** These tests cover individual components of the application in isolation.
    *   `test_services.py`: Tests the business logic in the service layer.
    *   `test_repositories.py`: Tests the data access logic in the repository layer using an in-memory SQLite database.
    *   `test_routers.py`: Tests the API routers to ensure they handle requests and responses correctly.

## Project Status

This project is currently in a transitional phase of refactoring from a monolithic structure with business logic in stored procedures to a modern, layered architecture with business logic in a Python-based service layer.

**Completed tasks:**
*   **Project Structure:** The codebase has been reorganized into a layered architecture (`server/api`, `server/domain`, etc.).
*   **Configuration:** Configuration management has been updated to use `pydantic-settings`.
*   **Core Services:** The services for Site and Crane management have been refactored to use the new repository and service pattern.
*   **E2E Tests:** A new End-to-End test suite has been created in `tests/e2e`. The test for the main business workflow (`test_workflow.py`) currently covers the refactored services (Site creation, approval, and Crane listing).
*   **Development Scripts:** A `scripts/dev.sh` script has been created to automate database setup and test execution.

**Next Steps / To-Do:**
*   **Complete Service Refactoring:** The remaining business logic (for assignments, documents, attendance, etc.) needs to be moved from `StoredProcedureService` to the new service layer.
*   **Complete E2E Workflow Test:** The `test_workflow.py` needs to be completed to cover all 9 steps of the business workflow as the services are refactored.
*   **Remove Stored Procedures:** Once all business logic is in the service layer, the stored procedures in `sql/procs.sql` can be removed.

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