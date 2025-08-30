import os
import sys
import psycopg2
from psycopg2 import sql

# This is a standalone script, so we need to set up the path
# to import from the server directory.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.db_seeder import seed_data
from server.database import db_manager

# --- Configuration ---
# Read connection details from environment variables
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")
DB_NAME = os.getenv("PGDATABASE", "craneops")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASS = os.getenv("PGPASSWORD", "admin")

# Define the order of SQL script execution
SQL_FILES = {
    "schema": "sql/01_schema.sql",
    "views": "sql/02_views.sql",
    "reset": "sql/03_reset.sql",
}

# --- Helper Functions ---

def print_color(message, color_code):
    """Prints a message in a given color."""
    print(f"\033[{color_code}m{message}\033[0m")

def print_success(message):
    print_color(f"✓ {message}", "32")  # Green

def print_error(message):
    print_color(f"✗ {message}", "31")  # Red

def print_info(message):
    print_color(f"  {message}", "34")  # Blue

def get_db_connection(dbname=DB_NAME):
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        # Handle case where the database doesn't exist yet
        if f'database "{dbname}" does not exist' in str(e):
            print_info(f"Database '{dbname}' not found. It will be created.")
            return None
        print_error(f"Could not connect to PostgreSQL: {e}")
        sys.exit(1)

def execute_sql_file(conn, file_path):
    """Executes the SQL commands from a given file."""
    if not os.path.exists(file_path):
        print_error(f"SQL file not found: {file_path}")
        return

    print_info(f"Executing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    with conn.cursor() as cur:
        try:
            cur.execute(sql_script)
            conn.commit()
            print_success(f"Successfully executed {file_path}")
        except Exception as e:
            conn.rollback()
            print_error(f"Error executing {file_path}: {e}")
            sys.exit(1)

def create_database_if_not_exists():
    """
    Connects to the default 'postgres' database to create the target database
    if it doesn't already exist.
    """
    conn = get_db_connection(dbname="postgres")
    if conn is None:
        print_error("Failed to connect to 'postgres' database to perform initial setup.")
        sys.exit(1)

    conn.autocommit = True
    with conn.cursor() as cur:
        # Check if the database exists
        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [DB_NAME])
        exists = cur.fetchone()
        if not exists:
            print_info(f"Creating database: {DB_NAME}")
            try:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
                print_success(f"Database '{DB_NAME}' created.")
            except Exception as e:
                print_error(f"Failed to create database: {e}")
                sys.exit(1)
        else:
            print_info(f"Database '{DB_NAME}' already exists.")
    conn.close()

# --- Main Execution Logic ---

def run_db_init():
    """Initializes the database: creates schema and tables."""
    create_database_if_not_exists()
    conn = get_db_connection()
    if conn:
        execute_sql_file(conn, SQL_FILES["schema"])
        conn.close()

def run_procedural_seed():
    """Seeds the database with initial data using the procedural script."""
    print_info("Running procedural seed...")
    with db_manager.get_session() as db:
        try:
            seed_data(db)
            print_success("Procedural seeding complete.")
        except Exception as e:
            print_error(f"An error occurred during procedural seeding: {e}")
            db.rollback()
            sys.exit(1)

def run_db_reset():
    """Resets the database by truncating tables and reseeding."""
    conn = get_db_connection()
    if conn:
        execute_sql_file(conn, SQL_FILES["reset"])
        conn.close()
    run_procedural_seed()

def run_full_setup():
    """Runs the full database setup: init, views, truncate, seed."""
    print_info("Starting full database setup...")
    run_db_init()
    conn = get_db_connection()
    if conn:
        execute_sql_file(conn, SQL_FILES["views"])
        execute_sql_file(conn, SQL_FILES["reset"])
        conn.close()
    run_procedural_seed()
    print_success("Full database setup complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        print_info(f"Executing command: {command}")
        if command == "init":
            run_db_init()
        elif command == "seed":
            run_procedural_seed()
        elif command == "reset":
            run_db_reset()
        elif command == "full":
            run_full_setup()
        else:
            print_error(f"Unknown command: {command}")
            print_info("Available commands: init, seed, reset, full")
    else:
        print_info("No command provided. Running full setup by default.")
        run_full_setup()
