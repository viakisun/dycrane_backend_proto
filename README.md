# DY Crane Safety Management API

Welcome to the DY Crane Safety Management project! This repository contains the backend API and a frontend interactive test client for a comprehensive crane safety management system.

The primary goal of this project is to provide a robust, well-documented, and maintainable system for managing construction sites, cranes, drivers, and safety documents. A key feature is the **Developer Guide Test Client**, which serves as a living, interactive form of documentation for the entire business workflow.

## Project Documentation

This project is documented across several files to provide clear, targeted information for different needs:

-   **[README.md](README.md)** (You are here): High-level overview and project entry point.
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: The essential guide for developers. Contains detailed instructions on setting up your local environment, running the application, and contributing to the project.
-   **[TEST_CLIENT_GUIDE.md](TEST_CLIENT_GUIDE.md)**: A detailed guide to the interactive `/test-client`, explaining each step of the business workflow (A1-F2) and how to use the UI.
-   **[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)**: A sequence diagram that visually represents the entire end-to-end workflow.
-   **[openapi.yaml](openapi.yaml)**: The full OpenAPI (Swagger) specification for the backend API.
-   **[RELEASES.md](RELEASES.md)**: Contains release notes and a summary of changes for each version.

## Quick Start

For the full development setup guide, please see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Here is a brief overview of the steps:

1.  **Prerequisites**: Ensure you have Git, PostgreSQL, Python 3.8+, and Node.js 16+ installed.
2.  **Clone & Configure**:
    ```sh
    git clone https://github.com/your-username/dycrane_backend_proto.git
    cd dycrane_backend_proto
    cp .env.example .env
    # Edit .env with your PostgreSQL details
    ```
3.  **Initialize & Seed Database**:
    This command sets up the Python virtual environment, installs dependencies, creates the database, and seeds it with master data.
    ```sh
    ./scripts/dev.sh db/full
    ```
4.  **Run Backend Server**:
    ```sh
    .venv/bin/uvicorn server.main:app --reload
    # API is now running on http://localhost:8000
    ```
5.  **Run Frontend Dev Server**:
    In a new terminal:
    ```sh
    cd client
    npm install
    npm run dev
    # Frontend is now running on http://localhost:3000
    ```

## Using the Developer Guide Test Client

Navigate to `http://localhost:3000/test-client` in your browser to access the interactive workflow tool.

-   **Purpose**: To visualize, test, and understand the end-to-end business logic.
-   **"Auto Run All"**: Executes the entire A1-F2 workflow.
-   **"Reset Workflow Data"**: Before running the workflow, especially for a second time, press this button. It clears all previous transactional data from the server to prevent `409 Conflict` errors.

For a full explanation of each step and how to use the client, please read the **[TEST_CLIENT_GUIDE.md](TEST_CLIENT_GUIDE.md)**.

## Project Structure

The project is organized into a layered architecture for the backend and a modern component-based structure for the frontend.

-   `server/`: Python FastAPI backend.
    -   `api/`: API routers and endpoints.
    -   `domain/`: Core business logic, schemas, and database models.
    -   `sql/`: Database schema and reset scripts.
-   `client/`: TypeScript React frontend (Vite).
    -   `src/pages/test-client/`: The source code for the developer guide test client.
-   `scripts/`: Helper scripts for development and database management.
-   `tests/`: E2E and unit tests.

We encourage you to read **[CONTRIBUTING.md](CONTRIBUTING.md)** for a deeper dive into the project structure and our development practices.