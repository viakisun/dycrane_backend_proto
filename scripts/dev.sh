#!/bin/bash

# Exit on any error
set -e

# --- Configuration ---
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
VENV_PATH="$PROJECT_ROOT/.venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
DOTENV_FILE="$PROJECT_ROOT/.env"

# --- Helper Functions ---
step() {
    echo -e "\n=================================================="
    echo -e "[STEP] $1"
    echo -e "=================================================="
}

sub_step() {
    echo -e "[INFO] $1"
}

success() {
    echo -e "[OK] $1"
}

failure() {
    echo -e "[FAIL] $1"
    exit 1
}

# --- Prerequisite Checks ---
activate_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        sub_step "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_PATH"
        if [ $? -ne 0 ]; then
            failure "Failed to create virtual environment."
        fi
    fi

    sub_step "Installing/updating dependencies from $REQUIREMENTS_FILE..."
    "$VENV_PATH/bin/pip" install -r "$REQUIREMENTS_FILE" --upgrade
    if [ $? -ne 0 ]; then
        failure "Failed to install dependencies."
    fi
    success "Virtual environment is ready."
}

# --- Database Operations ---
initialize_database() {
    step "Initializing Database"
    "$VENV_PATH/bin/python" "$PROJECT_ROOT/scripts/db_cli.py" "full"
    if [ $? -ne 0 ]; then
        failure "Database initialization failed with Python runner."
    fi
    success "Database initialized successfully."
}

# --- Linter & Type Checker ---
run_linting() {
    step "Running Linters and Type Checkers"
    sub_step "Running ruff check..."
    "$VENV_PATH/bin/ruff" check "$PROJECT_ROOT/server"
    sub_step "Running mypy..."
    "$VENV_PATH/bin/mypy" "$PROJECT_ROOT/server"
    success "All static analysis checks passed."
}

# --- Test Execution ---
run_tests() {
    step "Running E2E Tests"
    SERVER_PID=""

    # Cleanup function to ensure server is stopped
    cleanup() {
        if [ ! -z "$SERVER_PID" ]; then
            sub_step "Stopping API server (PID: $SERVER_PID)..."
            kill $SERVER_PID
            success "Server stopped."
        fi
    }
    trap cleanup EXIT

    # 1. Start API server in the background
    sub_step "Starting API server in background..."
    "$VENV_PATH/bin/uvicorn" server.main:app --host 127.0.0.1 --port 8000 &
    SERVER_PID=$!
    sub_step "Server started with PID: $SERVER_PID"

    # 2. Health Check Polling
    sub_step "Waiting for server to be healthy at http://127.0.0.1:8000/api/health..."
    TIMEOUT=60
    INTERVAL=0.5
    ELAPSED=0
    while [ $ELAPSED -lt $TIMEOUT ]; do
        response_code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/health)
        if [ "$response_code" -eq 200 ]; then
            success "Server is healthy."
            break
        fi
        sleep $INTERVAL
        ELAPSED=$(echo "$ELAPSED + $INTERVAL" | bc)
    done

    if [ $ELAPSED -ge $TIMEOUT ]; then
        failure "Server did not become healthy within $TIMEOUT seconds."
    fi

    # 3. Run Pytest
    pytest_args="tests/e2e"
    if [ "$1" == "test/verbose" ]; then
        pytest_args="$pytest_args -vv -s --log-cli-level=INFO"
    else
        pytest_args="$pytest_args -q"
    fi

    sub_step "Executing pytest with arguments: $pytest_args"
    "$VENV_PATH/bin/pytest" $pytest_args
    if [ $? -ne 0 ]; then
        failure "Pytest reported test failures."
    else
        success "All tests passed!"
    fi
}

# --- Main Logic ---
if [ -f "$DOTENV_FILE" ]; then
    export $(grep -v '^#' "$DOTENV_FILE" | xargs)
fi

activate_venv

case "$1" in
    "db")
        initialize_database
        ;;
    "lint")
        run_linting
        ;;
    "test" | "test/verbose")
        initialize_database
        run_tests "$1"
        ;;
    *)
        echo "Usage: $0 {db|lint|test|test/verbose}"
        exit 1
        ;;
esac

echo -e "\nCommand '$1' completed."
