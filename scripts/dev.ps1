# =============================================================================
# DY Crane Safety Management - Development & Test Orchestrator (PowerShell)
#
# USAGE:
#   ./scripts/dev.ps1 -Command db
#   ./scripts/dev.ps1 -Command test
#   ./scripts/dev.ps1 -Command test/verbose
# =============================================================================

param (
    [Parameter(Mandatory = $true)]
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
        if ($_ -match "^\s*#") { return }
        $name, $value = $_.Split('=', 2)
        if ($name -and $value) {
            [System.Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), "Process")
        }
    }
}

if ($env:API_HOST) { $API_HOST = $env:API_HOST } else { $API_HOST = "127.0.0.1" }
if ($env:API_PORT) { $API_PORT = $env:API_PORT } else { $API_PORT = 8000 }
if ($env:E2E_BASE_URL) { $BASE_URL = $env:E2E_BASE_URL } else { $BASE_URL = "http://$($API_HOST):$($API_PORT)" }
$HEALTH_URL = "$($BASE_URL)/api/health"

# --- Helper Functions ---
function Write-Step($Message) {
    Write-Host "`n" + ("=" * 60)
    Write-Host "[STEP] $Message" -ForegroundColor Yellow
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
    if ($ExitCode -ne 0) { exit $ExitCode }
}

# --- Prerequisite Checks ---
function Test-Psql {
    return (Get-Command psql -ErrorAction SilentlyContinue) -ne $null
}

function Activate-Venv {
    if (-not (Test-Path $VenvPath)) {
        Write-SubStep "Virtual environment not found. Creating..."
        python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) { Write-Failure "Failed to create venv." }
    }
    . (Join-Path $VenvPath "Scripts/Activate.ps1")
    Write-SubStep "Installing dependencies..."
    pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) { Write-Failure "Failed to install dependencies." }
    Write-Success "Virtual environment is ready."
}

# --- Database Operations ---
function Initialize-Database {
    Write-Step "Initializing Database"
    if (Test-Psql) {
        Write-SubStep "Using psql for database operations."
        $env:PGPASSWORD = $env:PGPASSWORD
        # Attempt to create DB, suppress errors if it exists
        psql -h $env:PGHOST -U $env:PGUSER -d "postgres" -c "CREATE DATABASE $($env:PGDATABASE)" 2>$null

        psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/init_db.sql"
        psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/init_view.sql"
        psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/truncate.sql"
        psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -v ON_ERROR_STOP=1 -f "$ProjectRoot/sql/seed.sql"
    } else {
        Write-SubStep "psql not found, falling back to Python runner."
        python "$ProjectRoot/scripts/db_runner.py" "full"
    }

    if ($LASTEXITCODE -ne 0) { Write-Failure "Database initialization failed." }
    Write-Success "Database initialized."
}

# --- Test Execution ---
function Run-Tests {
    param($IsVerbose)
    Write-Step "Running E2E Tests"
    $ServerProcess = $null
    try {
        Write-SubStep "Starting API server in background..."
        $ServerProcess = Start-Process python -ArgumentList "-m uvicorn", "server.main:app", "--host", $API_HOST, "--port", $API_PORT -PassThru -WindowStyle Hidden

        Write-SubStep "Waiting for server... (PID: $($ServerProcess.Id))"
        $Timeout = 60
        $Interval = 0.5
        $Timer = [System.Diagnostics.Stopwatch]::StartNew()
        while ($Timer.Elapsed.TotalSeconds -lt $Timeout) {
            try {
                $response = Invoke-WebRequest -Uri $HEALTH_URL -UseBasicParsing -TimeoutSec 1
                if ($response.StatusCode -eq 200) { Write-Success "Server is healthy."; break }
            } catch { Start-Sleep -Seconds $Interval }
        }
        if ($Timer.Elapsed.TotalSeconds -ge $Timeout) { Write-Failure "Server health check timed out." }

        $pytest_args = if ($IsVerbose) { @("tests/e2e", "-vv", "-s") } else { @("tests/e2e", "-q") }
        Write-SubStep "Executing: pytest $($pytest_args -join ' ')"
        pytest $pytest_args
        if ($LASTEXITCODE -ne 0) { Write-Failure "Tests failed." } else { Write-Success "All tests passed!" }
    }
    finally {
        if ($ServerProcess) {
            Write-SubStep "Stopping server (PID: $($ServerProcess.Id))"
            Stop-Process -Id $ServerProcess.Id -Force
        }
    }
}

# --- Main Logic ---
if (-not ($env:PGHOST -and $env:PGUSER -and $env:PGPASSWORD -and $env:PGDATABASE)) {
    Write-Failure "Database env vars (PGHOST, PGUSER, PGPASSWORD, PGDATABASE) not set."
}

Activate-Venv

switch ($Command) {
    "db" { Initialize-Database }
    "test" { Initialize-Database; Run-Tests -IsVerbose $false }
    "test/verbose" { Initialize-Database; Run-Tests -IsVerbose $true }
}

Write-Success "Command '$Command' completed."