param(
    [Parameter(Position=0)]
    [ValidateSet("db:init", "db:views", "db:procs", "db:seed", "db:reset", "db:rebuild", "api:run", "test:run", "test:verbose", "status", "help")]
    [string]$Command = "help"
)

# Configuration
$DB_HOST = "localhost"
$DB_PORT = "5432" 
$DB_USER = "postgres"
$DB_PASS = "admin"
$DB_NAME = "craneops"
$API_PORT = "8000"

# Database connection
$PG_URL = "postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
$env:DATABASE_URL = "postgresql+psycopg2://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
$env:PGPASSWORD = $DB_PASS

function Write-Step($Message) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan
}

function Write-Success($Message) {
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Failure($Message) {
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info($Message) {
    Write-Host "  $Message" -ForegroundColor Gray
}

function Test-Prerequisites {
    Write-Step "Checking prerequisites"
    
    # Test psql
    try {
        $null = & psql --version 2>&1
        Write-Success "PostgreSQL client available"
    }
    catch {
        Write-Failure "psql command not found"
        Write-Host "Install PostgreSQL client tools"
        exit 1
    }
    
    # Test database connection
    try {
        $result = & psql $PG_URL -c "SELECT 1;" -t 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database connection working"
        } else {
            Write-Failure "Cannot connect to database"
            Write-Info "Connection: $PG_URL"
            Write-Host $result
            exit 1
        }
    }
    catch {
        Write-Failure "Database connection failed: $($_.Exception.Message)"
        exit 1
    }
    
    # Test Python
    if ($Command -eq "api:run" -or $Command -like "test:*") {
        try {
            $pythonVersion = & python --version 2>&1
            Write-Success "Python available: $pythonVersion"
            
            # Check key packages
            $packages = @("fastapi", "sqlalchemy", "psycopg2", "pytest")
            foreach ($pkg in $packages) {
                try {
                    $null = & python -c "import $pkg" 2>&1
                    if ($LASTEXITCODE -ne 0) {
                        Write-Failure "Missing Python package: $pkg"
                        Write-Host "Run: pip install $pkg"
                        exit 1
                    }
                }
                catch {
                    Write-Failure "Cannot check Python package: $pkg"
                    exit 1
                }
            }
            Write-Success "Required Python packages available"
        }
        catch {
            Write-Failure "Python not available"
            exit 1
        }
    }
}

function Execute-SqlFile($FilePath, $Description) {
    if (-not (Test-Path $FilePath)) {
        Write-Failure "SQL file not found: $FilePath"
        exit 1
    }
    
    Write-Step "Executing $Description"
    try {
        $output = & psql $PG_URL -v ON_ERROR_STOP=1 -f $FilePath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success $Description
            
            # Extract meaningful output
            $notices = $output | Where-Object { $_ -match "NOTICE:" }
            foreach ($notice in $notices | Select-Object -First 3) {
                $cleaned = $notice -replace "NOTICE:\s*", ""
                Write-Info $cleaned
            }
        } else {
            Write-Failure "$Description failed"
            Write-Host $output
            exit 1
        }
    }
    catch {
        Write-Failure "Error executing $FilePath`: $($_.Exception.Message)"
        exit 1
    }
}

function Show-DatabaseInfo {
    Write-Step "Database status"
    
    try {
        # Schema check
        $schemaExists = & psql $PG_URL -c "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'ops');" -t 2>&1
        if ($schemaExists -match "t") {
            Write-Success "Schema 'ops' exists"
        } else {
            Write-Info "Schema 'ops' not found"
            return
        }
        
        # Count objects
        $tables = & psql $PG_URL -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'ops';" -t 2>&1
        $functions = & psql $PG_URL -c "SELECT COUNT(*) FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'ops';" -t 2>&1  
        $views = & psql $PG_URL -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'ops';" -t 2>&1
        $users = & psql $PG_URL -c "SELECT COUNT(*) FROM ops.users;" -t 2>&1
        
        Write-Info "Tables: $($tables.Trim())"
        Write-Info "Functions: $($functions.Trim())"
        Write-Info "Views: $($views.Trim())"
        Write-Info "Users: $($users.Trim())"
        
    } catch {
        Write-Info "Could not retrieve database status"
    }
}

function Show-Help {
    Write-Host @"
DY Crane Safety Management - Development Tools

USAGE:
  .\dev.ps1 <command>

DATABASE COMMANDS:
  db:init      Initialize schema, tables, triggers
  db:views     Create enhanced views and query functions  
  db:procs     Install stored procedures for business logic
  db:seed      Load test data
  db:reset     Quick reset: truncate + init + seed
  db:rebuild   Full rebuild: truncate + init + views + procs + seed

APPLICATION COMMANDS:
  api:run      Start FastAPI development server
  test:run     Run test suite (pytest mode)
  test:verbose Run test suite with detailed output

UTILITY COMMANDS:
  status       Show database and system status
  help         Show this help

CONFIGURATION:
  Database: $PG_URL
  API Port: $API_PORT

WORKFLOW:
  1. .\dev.ps1 db:rebuild    # Set up database
  2. .\dev.ps1 test:verbose  # Verify system
  3. .\dev.ps1 api:run       # Start development

"@
}

# Main execution
switch ($Command) {
    "db:init" {
        Test-Prerequisites
        Execute-SqlFile "init_db.sql" "Database schema initialization"
        Show-DatabaseInfo
    }
    
    "db:views" {
        Test-Prerequisites  
        Execute-SqlFile "init_view.sql" "Enhanced views and query functions"
        Show-DatabaseInfo
    }
    
    "db:procs" {
        Test-Prerequisites
        Execute-SqlFile "procs.sql" "Stored procedures and business logic"
        Show-DatabaseInfo
    }
    
    "db:seed" {
        Test-Prerequisites
        Execute-SqlFile "seed.sql" "Test data loading"
        Show-DatabaseInfo
    }
    
    "db:reset" {
        Test-Prerequisites
        Write-Step "Quick database reset"
        Execute-SqlFile "truncate.sql" "Data cleanup"
        Execute-SqlFile "init_db.sql" "Schema initialization"  
        Execute-SqlFile "seed.sql" "Test data loading"
        Show-DatabaseInfo
        Write-Success "Database reset complete"
    }
    
    "db:rebuild" {
        Test-Prerequisites
        Write-Step "Full database rebuild"
        Execute-SqlFile "truncate.sql" "Data cleanup"
        Execute-SqlFile "init_db.sql" "Schema initialization"
        Execute-SqlFile "init_view.sql" "Enhanced views" 
        Execute-SqlFile "procs.sql" "Stored procedures"
        Execute-SqlFile "seed.sql" "Test data loading"
        Show-DatabaseInfo
        Write-Success "Database rebuild complete"
    }
    
    "api:run" {
        Test-Prerequisites
        Write-Step "Starting FastAPI server"
        Write-Info "Server: http://127.0.0.1:$API_PORT"
        Write-Info "Docs: http://127.0.0.1:$API_PORT/docs"
        Write-Info "Press Ctrl+C to stop"
        Write-Host ""
        
        try {
            & python app.py
        }
        catch {
            Write-Failure "Failed to start server: $($_.Exception.Message)"
            exit 1
        }
    }
    
    "test:run" {
        Test-Prerequisites
        Write-Step "Running test suite (pytest mode)"
        
        try {
            $start = Get-Date
            & pytest -q test.py
            $duration = ((Get-Date) - $start).TotalSeconds
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "All tests passed ($([math]::Round($duration, 1))s)"
            } else {
                Write-Failure "Tests failed"
                exit 1
            }
        }
        catch {
            Write-Failure "Test execution error: $($_.Exception.Message)"
            exit 1
        }
    }
    
    "test:verbose" {
        Test-Prerequisites
        Write-Step "Running test suite (verbose mode)"
        Write-Host ""
        
        try {
            $start = Get-Date
            & python test.py
            $duration = ((Get-Date) - $start).TotalSeconds
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Success "All tests completed ($([math]::Round($duration, 1))s)"
            } else {
                Write-Failure "Test execution failed"
                exit 1
            }
        }
        catch {
            Write-Failure "Test execution error: $($_.Exception.Message)"
            exit 1
        }
    }
    
    "status" {
        Test-Prerequisites
        Show-DatabaseInfo
        
        # Check SQL files
        Write-Step "SQL files"
        $sqlFiles = @("init_db.sql", "init_view.sql", "procs.sql", "seed.sql", "truncate.sql")
        foreach ($file in $sqlFiles) {
            if (Test-Path $file) {
                Write-Success "$file present"
            } else {
                Write-Failure "$file missing"
            }
        }
        
        # Check app files  
        Write-Step "Application files"
        if (Test-Path "app.py") {
            Write-Success "app.py present"
        } else {
            Write-Failure "app.py missing"
        }
        
        if (Test-Path "test.py") {
            Write-Success "test.py present"
        } else {
            Write-Failure "test.py missing"
        }
    }
    
    "help" {
        Show-Help
    }
    
    default {
        Write-Failure "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-Success "Command completed"