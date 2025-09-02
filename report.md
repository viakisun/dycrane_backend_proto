# API-Database Correlation Report

- **Generation Timestamp**: 2025-09-02 08:02:43
- **Database Type**: PostgreSQL

---

## 1. GET /api/v1/system/

- **Source File**: `server/api/routers/health.py`
- **Handler**: `health_check_endpoint`
- **Query Description**: Executes a raw SQL query to check database connectivity.
- **SQL Snippet**: `SELECT 1 as health_check`
- **Database Objects**:
  - **Unknown**: No specific table, view, or function is referenced.

---

## 2. POST /api/v1/system/tools/reset-transactional

- **Source File**: `server/api/routers/health.py`
- **Handler**: `reset_transactional_data_endpoint`
- **Query Description**: Executes the `sql/04_transactional_reset.sql` script to truncate transactional tables.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.requests` (TABLE, `01_schema.sql`)
  - `ops.site_crane_assignments` (TABLE, `01_schema.sql`)
  - `ops.driver_assignments` (TABLE, `01_schema.sql`)
  - `ops.driver_attendance` (TABLE, `01_schema.sql`)
  - `ops.driver_document_requests` (TABLE, `01_schema.sql`)
  - `ops.driver_document_items` (TABLE, `01_schema.sql`)

---

## 3. POST /api/v1/system/tools/reset-full

- **Source File**: `server/api/routers/health.py`
- **Handler**: `reset_full_database_for_testing_endpoint`
- **Query Description**: Executes the `sql/03_reset.sql` script to truncate all business tables.
- **Database Objects**:
  - `ops.driver_document_items` (TABLE, `01_schema.sql`)
  - `ops.driver_document_requests` (TABLE, `01_schema.sql`)
  - `ops.driver_attendance` (TABLE, `01_schema.sql`)
  - `ops.driver_assignments` (TABLE, `01_schema.sql`)
  - `ops.site_crane_assignments` (TABLE, `01_schema.sql`)
  - `ops.cranes` (TABLE, `01_schema.sql`)
  - `ops.user_orgs` (TABLE, `01_schema.sql`)
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.orgs` (TABLE, `01_schema.sql`)
  - `ops.users` (TABLE, `01_schema.sql`)

---

## 4. GET /api/v1/catalog/crane-models

- **Source File**: `server/api/routers/crane_models.py`
- **Handler**: `list_crane_models_endpoint`
- **Query Description**: Queries for all records in the `CraneModel` table.
- **Database Objects**:
  - `ops.crane_models` (TABLE, `01_schema.sql`)

---

## 5. POST /api/v1/org/sites

- **Source File**: `server/api/routers/sites.py`
- **Handler**: `create_site_endpoint`
- **Query Description**: Inserts a new record into the `sites` table after validating the requesting user exists.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.users` (TABLE, `01_schema.sql`)

---

## 6. GET /api/v1/org/sites

- **Source File**: `server/api/routers/sites.py`
- **Handler**: `list_sites_endpoint`
- **Query Description**: Selects records from the `sites` table.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)

---

## 7. PATCH /api/v1/org/sites/{site_id}

- **Source File**: `server/api/routers/sites.py`
- **Handler**: `update_site_endpoint`
- **Query Description**: Updates a record in the `sites` table after validating the approving user exists.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.users` (TABLE, `01_schema.sql`)

---

## 8. GET /api/v1/org/cranes

- **Source File**: `server/api/routers/cranes.py`
- **Handler**: `list_cranes_endpoint`
- **Query Description**: Selects records from the `cranes` table, joining with `crane_models`.
- **Database Objects**:
  - `ops.cranes` (TABLE, `01_schema.sql`)
  - `ops.crane_models` (TABLE, `01_schema.sql`)

---

## 9. GET /api/v1/org/owners/

- **Source File**: `server/api/routers/owners.py`
- **Handler**: `list_owners_endpoint`
- **Query Description**: Selects records from the `orgs` table, joining with `cranes` to get statistics.
- **Database Objects**:
  - `ops.orgs` (TABLE, `01_schema.sql`)
  - `ops.cranes` (TABLE, `01_schema.sql`)

---

## 10. GET /api/v1/org/owners/{ownerId}/cranes

- **Source File**: `server/api/routers/owners.py`
- **Handler**: `list_owner_cranes_endpoint`
- **Query Description**: Selects records from the `cranes` table, joining with `crane_models`. (Same as endpoint 8)
- **Database Objects**:
  - `ops.cranes` (TABLE, `01_schema.sql`)
  - `ops.crane_models` (TABLE, `01_schema.sql`)

---

## 11. POST /api/v1/ops/crane-deployments

- **Source File**: `server/api/routers/crane_assignments.py`
- **Handler**: `create_crane_assignment_endpoint`
- **Query Description**: Creates a new record in `site_crane_assignments` after validating the site and crane.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.cranes` (TABLE, `01_schema.sql`)
  - `ops.site_crane_assignments` (TABLE, `01_schema.sql`)

---

## 12. POST /api/v1/ops/driver-deployments

- **Source File**: `server/api/routers/driver_assignments.py`
- **Handler**: `create_driver_assignment_endpoint`
- **Query Description**: Creates a new record in `driver_assignments` after validating the crane assignment and driver.
- **Database Objects**:
  - `ops.site_crane_assignments` (TABLE, `01_schema.sql`)
  - `ops.users` (TABLE, `01_schema.sql`)
  - `ops.driver_assignments` (TABLE, `01_schema.sql`)

---

## 13. POST /api/v1/ops/driver-attendance-logs

- **Source File**: `server/api/routers/attendances.py`
- **Handler**: `create_attendance_endpoint`
- **Query Description**: Creates a new record in `driver_attendance` after validating the driver assignment.
- **Database Objects**:
  - `ops.driver_assignments` (TABLE, `01_schema.sql`)
  - `ops.driver_attendance` (TABLE, `01_schema.sql`)

---

## 14. POST /api/v1/compliance/document-requests

- **Source File**: `server/api/routers/document_requests.py`
- **Handler**: `create_document_request_endpoint`
- **Query Description**: Creates a new record in `driver_document_requests` after validating the site and driver.
- **Database Objects**:
  - `ops.sites` (TABLE, `01_schema.sql`)
  - `ops.users` (TABLE, `01_schema.sql`)
  - `ops.driver_document_requests` (TABLE, `01_schema.sql`)

---

## 15. POST /api/v1/compliance/document-items

- **Source File**: `server/api/routers/document_items.py`
- **Handler**: `submit_document_item_endpoint`
- **Query Description**: Creates a new record in `driver_document_items` after validating the document request.
- **Database Objects**:
  - `ops.driver_document_requests` (TABLE, `01_schema.sql`)
  - `ops.driver_document_items` (TABLE, `01_schema.sql`)

---

## 16. PATCH /api/v1/compliance/document-items/{item_id}

- **Source File**: `server/api/routers/document_items.py`
- **Handler**: `review_document_item_endpoint`
- **Query Description**: Updates a record in the `driver_document_items` table.
- **Database Objects**:
  - `ops.driver_document_items` (TABLE, `01_schema.sql`)

---

## 17. POST /api/v1/deploy/requests

- **Source File**: `server/api/routers/requests.py`
- **Handler**: `create_request_endpoint`
- **Query Description**: Creates a new record in the `requests` table.
- **Database Objects**:
  - `ops.requests` (TABLE, `01_schema.sql`)

---

## 18. POST /api/v1/deploy/requests/{requestId}/responses

- **Source File**: `server/api/routers/requests.py`
- **Handler**: `respond_to_request_endpoint`
- **Query Description**: Updates a record in the `requests` table.
- **Database Objects**:
  - `ops.requests` (TABLE, `01_schema.sql`)
