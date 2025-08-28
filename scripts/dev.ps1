# =============================================================================
# DY Crane Safety Management - Development & Test Orchestrator
#
# USAGE:
#   ./scripts/dev.ps1 db            - Initializes the database (tables, views, seeds).
#   ./scripts/dev.ps1 test          - Runs the full E2E test suite.
#   ./scripts/dev.ps1 test/verbose  - Runs E2E tests with detailed logging.
#
# REQUIREMENTS:
#   - PowerShell 7+
#   - Python 3.8+
#   - Docker (for PostgreSQL) or a running PostgreSQL instance.
#   - `psql` client (recommended) or `psycopg2` python package.
# =============================================================================

param (
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("db", "test", "test/verbose")]
    [string]$Command
)

# --- Configuration ---
$ProjectRoot = (Get-Item -Path $PSScriptRoot).Parent.FullName
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"
$DotEnvFile = Join-Path $ProjectRoot ".env"

# Load .env file if it exists
if (Test-Path $DotEnvFile) {
    Get-Content $DotEnvFile | ForEach-Object {
        if ($_ -match "^\s*#") { return } # Skip comments
        $name, $value = $_.Split('=', 2)
        if ($name -and $value) {
            [System.Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), "Process")
        }
    }
}

# API and Database settings from environment variables
$API_HOST = $env:API_HOST_OVERRIDE ?? $env:API_HOST ?? "127.0.0.1"
$API_PORT = $env:API_PORT_OVERRIDE ?? $env:API_PORT ?? 8000
$BASE_URL = $env:E2E_BASE_URL ?? "http://$($API_HOST):$($API_PORT)"
$HEALTH_URL = "$($BASE_URL)/health"

# --- Helper Functions ---

function Write-Step($Message) {
    Write-Host "`n" + ("=" * 60)
    Write-Host "[STEP] $Message"
    Write-Host ("=" * 60)
}

function Write-SubStep($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success($Message) {
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Failure($Message, $ExitCode = 1) {
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    if ($ExitCode -ne 0) {
        exit $ExitCode
    }
}

function Write-Warning($Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

# --- Prerequisite Checks ---

function Test-Psql {
    try {
        $null = psql --version 2>&1
        if ($LASTEXITCODE -eq 0) { return $true }
    }
    catch { }
    return $false
}

function Activate-Venv {
    if (-not (Test-Path $VenvPath)) {
        Write-SubStep "Virtual environment not found. Creating..."
        python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) { Write-Failure "Failed to create virtual environment." }
    }

    # Activate venv
    . (Join-Path $VenvPath "Scripts/Activate.ps1")

    Write-SubStep "Installing/updating dependencies from $RequirementsFile..."
    pip install -r $RequirementsFile --upgrade
    if ($LASTEXITCODE -ne 0) { Write-Failure "Failed to install dependencies." }
    Write-Success "Virtual environment is ready."
}

# --- Database Operations ---

function Initialize-Database {
    Write-Step "Initializing Database"

    if (Test-Psql) {
        Write-SubStep "Using psql for database operations."
        try {
            # Use postgres db to create the main database if it doesn't exist
            psql -h $env:PGHOST -U $env:PGUSER -d "postgres" -c "CREATE DATABASE $($env:PGDATABASE)" 2>$null

            psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/init_db.sql"
            psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/init_view.sql"
            psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/truncate.sql"
            psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/seed.sql"

            Write-Success "Database initialized successfully via psql."
        }
        catch {
            Write-Failure "Database initialization failed with psql. Error: $($_.Exception.Message)"
        }
    }
    else {
        Write-Warning "psql command not found. Falling back to Python DB runner."
        Write-SubStep "Ensure psycopg2-binary is installed."
        python "$ProjectRoot/scripts/db_runner.py" "full"
        if ($LASTEXITCODE -ne 0) { Write-Failure "Database initialization failed with Python runner." }
        Write-Success "Database initialized successfully via Python runner."
    }
}

# --- Test Execution ---

function Run-Tests {
    param($IsVerbose)

    Write-Step "Running E2E Tests"
    $ServerProcess = $null

    try {
        # 1. Start API server in the background
        Write-SubStep "Starting API server in background..."
        $ServerProcess = Start-Process python -ArgumentList "-m uvicorn", "server.main:app", "--host", $API_HOST, "--port", $API_PORT -PassThru -WindowStyle Hidden
        Write-SubStep "Server started with PID: $($ServerProcess.Id)"

        # 2. Health Check Polling
        Write-SubStep "Waiting for server to be healthy at $HEALTH_URL..."
        $Timeout = 60 # seconds
        $Interval = 0.5 # seconds
        $Timer = [System.Diagnostics.Stopwatch]::StartNew()

        while ($Timer.Elapsed.TotalSeconds -lt $Timeout) {
            try {
                $response = Invoke-WebRequest -Uri $HEALTH_URL -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    Write-Success "Server is healthy."
                    break
                }
            }
            catch {
                Start-Sleep -Seconds $Interval
            }
        }

        if ($Timer.Elapsed.TotalSeconds -ge $Timeout) {
            Write-Failure "Server did not become healthy within $Timeout seconds."
        }

        # 3. Run Pytest
        $pytest_args = @("tests/e2e", "-q")
        if ($IsVerbose) {
            $pytest_args = @("tests/e2e", "-vv", "-s", "--log-cli-level=INFO")
        }

        Write-SubStep "Executing pytest with arguments: $($pytest_args -join ' ')"
        pytest $pytest_args
        if ($LASTEXITCODE -ne 0) {
            Write-Failure "Pytest reported test failures."
        } else {
            Write-Success "All tests passed!"
        }
    }
    finally {
        # 4. Stop Server
        if ($ServerProcess) {
            Write-SubStep "Stopping API server (PID: $($ServerProcess.Id))..."
            Stop-Process -Id $ServerProcess.Id -Force
            Write-Success "Server stopped."
        }
    }
}

# --- Main Logic ---

# Check for required environment variables
if (-not $env:PGHOST -or -not $env:PGUSER -or -not $env:PGPASSWORD -or -not $env:PGDATABASE) {
    Write-Failure "Database environment variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE) are not set. Create a .env file or set them manually."
}

# Activate virtual environment and install dependencies
Activate-Venv

# Execute command
switch ($Command) {
    "db" {
        Initialize-Database
    }
    "test" {
        Initialize-Database
        Run-Tests -IsVerbose $false
    }
    "test/verbose" {
        Initialize-Database
        Run-Tests -IsVerbose $true
    }
}

Write-Host "`n"
Write-Success "Command '$Command' completed."