---
title: "Generate API–Database Correlation Report"
version: "1.0.0"
last_reviewed: "2025-09-03"
owner: "@jules"
inputs_required:
  - "Full source code access (FastAPI)"
  - "SQL schema definition files (`.sql`)"
expected_output:
  format: "Markdown (report.md)"
  sections:
    - "Endpoint-to-Table Mapping"
    - "Endpoint-to-View Mapping"
    - "Endpoint-to-Function/Procedure Mapping"
    - "Unresolved References"
constraints:
  - "Must perform static analysis only (no live DB execution)"
  - "Must cross-reference the defining SQL file for each DB object"
---

# AI Prompt — Generate API–Database Correlation Report (Markdown)

You are an assistant analyzing a project that contains both **API source code** and **SQL definition files** (such as `init_db.sql`, `init_view.sql`, and other files defining tables, views, functions, and stored procedures).

Your task is to produce a **single Markdown report (`report.md`)** that maps every API endpoint to the database objects it references.

---

## Step 1. Collect API Endpoints

* Identify all API endpoints defined in the project.
* For each endpoint, record:

  * HTTP method (GET, POST, etc.)
  * Path (e.g., `/api/cranes`)
  * Source file and handler function name

---

## Step 2. Extract Database Usage

* Inspect the handler logic to detect:

  * SQL queries written directly in code
  * ORM queries (e.g., SQLAlchemy)
  * Calls to functions, procedures, or views
* Normalize the extracted database identifiers.

---

## Step 3. Parse SQL Files

* Read the SQL files provided in the project.
* Identify definitions for:

  * `CREATE TABLE` → Tables
  * `CREATE VIEW` / `CREATE MATERIALIZED VIEW` → Views
  * `CREATE FUNCTION` → Functions
  * `CREATE PROCEDURE` → Procedures
* Build a dictionary of available database objects.

---

## Step 4. Correlate APIs to Database Objects

* Match the database identifiers used in API handlers to the definitions found in the SQL files.
* If a match exists, classify the object as TABLE, VIEW, FUNCTION, or PROCEDURE, and note the source SQL file.
* If unresolved, mark as **Unknown** but include the raw SQL or reference string.

---

## Step 5. Generate the Markdown Report

Output the final deliverable in **Markdown format** with the following structure:

* Title and metadata (generation timestamp, DB type).
* One section per API endpoint containing:

  * HTTP method and path
  * Source file and handler name
  * Extracted SQL or query description (inline, no code fences)
  * Database objects referenced (with type and originating SQL file)
  * Notes for skipped or unresolved items

---

## Step 6. Completion Criteria

The task is complete when the Markdown report satisfies all of the following:

* A file named `report.md` is generated.
* Every API endpoint is documented with its method, path, and handler.
* At least one SQL snippet or reference is listed for each endpoint (if available).
* Database objects (TABLE, VIEW, FUNCTION, PROCEDURE) are identified and classified.
* Cross-references to the defining SQL file are included.
* Unresolved or ambiguous cases are explicitly documented as **Unknown**.
* No live database execution is required — all information must come from static analysis of code and SQL files.
