# API–Database Correlation Report

*   **Generated at**: 2025-09-03 10:05:00 UTC
*   **Database Type**: PostgreSQL
*   **Analysis Method**: Static code and schema analysis

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### `POST /api/v1/auth/login`
-   **Handler**: `login_for_access_token` in `server/auth/routes.py`
-   **Query**: `user_repo.get_by_email(db, email=...)`
-   **DB Objects**:
    -   `TABLE`: `ops.users` (from `User` model in `user_repo`) - `sql/01_schema.sql`

### `POST /api/v1/auth/refresh`
-   **Handler**: `refresh_access_token` in `server/auth/routes.py`
-   **Query**: No database access. Operates on user context from token.
-   **DB Objects**: None

### `POST /api/v1/auth/logout`
-   **Handler**: `logout` in `server/auth/routes.py`
-   **Query**: No database access.
-   **DB Objects**: None

---

## 2. User Profile Endpoints (`/api/v1/me`)

### `GET /api/v1/me`
-   **Handler**: `read_current_user` in `server/users/routes_me.py`
-   **Query**: No database access. Returns data from user context.
-   **DB Objects**: None

### `GET /api/v1/me/permissions`
-   **Handler**: `read_current_user_permissions` in `server/users/routes_me.py`
-   **Query**: No database access. Returns hardcoded permissions based on roles.
-   **DB Objects**: None

### `GET /api/v1/me/bootstrap`
-   **Handler**: `get_bootstrap_data` in `server/users/routes_me.py`
-   **Query**: No database access. Returns hardcoded data.
-   **DB Objects**: None

---

## 3. System Endpoints (`/api/v1/system`)

### `GET /api/v1/system/`
-   **Handler**: `health_check_endpoint` in `server/api/routers/health.py`
-   **Query**: `session.execute(text("SELECT 1 as health_check"))`
-   **DB Objects**:
    -   **Unknown**: Performs a raw SQL query `SELECT 1` to check connectivity. Does not touch a specific table.

### `POST /api/v1/system/tools/reset-transactional`
-   **Handler**: `reset_transactional_data_endpoint` in `server/api/routers/health.py`
-   **Query**: `db_manager.reset_transactional_data()` which executes `sql/04_transactional_reset.sql`.
-   **DB Objects**:
    -   **TABLE**: `ops.sites`, `ops.site_crane_assignments`, `ops.driver_assignments`, etc. (via TRUNCATE) - `sql/01_schema.sql`

### `POST /api/v1/system/tools/reset-full`
-   **Handler**: `reset_full_database_for_testing_endpoint` in `server/api/routers/health.py`
-   **Query**: `db_manager.reset_full_database()` which executes `sql/03_reset.sql`.
-   **DB Objects**:
    -   **TABLE**: All tables in `ops` schema (via TRUNCATE) - `sql/01_schema.sql`

---

## 4. Catalog Endpoints (`/api/v1/catalog`)

### `GET /api/v1/catalog/crane-models`
-   **Handler**: `list_crane_models_endpoint` in `server/api/routers/crane_models.py`
-   **Query**: `crane_model_service.get_models()` -> `crane_model_repo.get_multi()`
-   **DB Objects**:
    -   `TABLE`: `ops.crane_models` (from `CraneModel` model) - `sql/01_schema.sql`

---

## 5. Organization Endpoints (`/api/v1/org`)

### `POST /api/v1/org/sites`
-   **Handler**: `create_site_endpoint` in `server/api/routers/sites.py`
-   **Query**: `site_service.create_site()` -> `site_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.sites` (from `Site` model) - `sql/01_schema.sql`

### `GET /api/v1/org/sites`
-   **Handler**: `list_sites_endpoint` in `server/api/routers/sites.py`
-   **Query**: `site_service.list_sites()` -> `site_repo.get_multi_for_user()`
-   **DB Objects**:
    -   `TABLE`: `ops.sites` (from `Site` model) - `sql/01_schema.sql`

### `PATCH /api/v1/org/sites/{site_id}`
-   **Handler**: `update_site_endpoint` in `server/api/routers/sites.py`
-   **Query**: `site_service.update_site()` -> `site_repo.update()`
-   **DB Objects**:
    -   `TABLE`: `ops.sites` (from `Site` model) - `sql/01_schema.sql`

### `GET /api/v1/org/cranes`
-   **Handler**: `list_cranes_endpoint` in `server/api/routers/cranes.py`
-   **Query**: `crane_service.list_owner_cranes()` -> `crane_repo.get_by_owner()`
-   **DB Objects**:
    -   `TABLE`: `ops.cranes` (from `Crane` model) - `sql/01_schema.sql`
    -   `TABLE`: `ops.crane_models` (via JOIN in `crane_repo`) - `sql/01_schema.sql`

### `GET /api/v1/org/owners/`
-   **Handler**: `list_owners_endpoint` in `server/api/routers/owners.py`
-   **Query**: `owner_service.get_owners_with_stats()`
-   **DB Objects**:
    -   `TABLE`: `ops.orgs` (from `Org` model) - `sql/01_schema.sql`
    -   `TABLE`: `ops.cranes` (from `Crane` model, via JOIN) - `sql/01_schema.sql`

### `GET /api/v1/org/owners/{ownerId}/cranes`
-   **Handler**: `list_owner_cranes_endpoint` in `server/api/routers/owners.py`
-   **Query**: `crane_service.list_owner_cranes()` -> `crane_repo.get_by_owner()`
-   **DB Objects**:
    -   `TABLE`: `ops.cranes` (from `Crane` model) - `sql/01_schema.sql`
    -   `TABLE`: `ops.crane_models` (via JOIN in `crane_repo`) - `sql/01_schema.sql`

---

## 6. Operations Endpoints (`/api/v1/ops`)

### `POST /api/v1/ops/crane-deployments`
-   **Handler**: `create_crane_assignment_endpoint` in `server/api/routers/crane_assignments.py`
-   **Query**: `assignment_service.assign_crane_to_site()` -> `site_crane_assignment_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.site_crane_assignments` (from `SiteCraneAssignment` model) - `sql/01_schema.sql`

### `POST /api/v1/ops/driver-deployments`
-   **Handler**: `create_driver_assignment_endpoint` in `server/api/routers/driver_assignments.py`
-   **Query**: `assignment_service.assign_driver_to_crane()` -> `driver_assignment_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.driver_assignments` (from `DriverAssignment` model) - `sql/01_schema.sql`

### `POST /api/v1/ops/driver-attendance-logs`
-   **Handler**: `create_attendance_endpoint` in `server/api/routers/attendances.py`
-   **Query**: `attendance_service.record_attendance()` -> `attendance_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.driver_attendance` (from `DriverAttendance` model) - `sql/01_schema.sql`

---

## 7. Compliance Endpoints (`/api/v1/compliance`)

### `POST /api/v1/compliance/document-requests`
-   **Handler**: `create_document_request_endpoint` in `server/api/routers/document_requests.py`
-   **Query**: `document_service.create_document_request()` -> `document_request_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.driver_document_requests` (from `DriverDocumentRequest` model) - `sql/01_schema.sql`

### `POST /api/v1/compliance/document-items`
-   **Handler**: `submit_document_item_endpoint` in `server/api/routers/document_items.py`
-   **Query**: `document_service.submit_document_item()` -> `document_item_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.driver_document_items` (from `DriverDocumentItem` model) - `sql/01_schema.sql`

### `POST /api/v1/compliance/document-items/{item_id}/review`
-   **Handler**: `review_document_item_endpoint` in `server/api/routers/document_items.py`
-   **Query**: `document_service.review_document_item()` -> `document_item_repo.update()`
-   **DB Objects**:
    -   `TABLE`: `ops.driver_document_items` (from `DriverDocumentItem` model) - `sql/01_schema.sql`

---

## 8. Deployment Endpoints (`/api/v1/deploy`)

### `POST /api/v1/deploy/requests`
-   **Handler**: `create_request_endpoint` in `server/api/routers/requests.py`
-   **Query**: `request_service.create_request()` -> `request_repo.create()`
-   **DB Objects**:
    -   `TABLE`: `ops.requests` (from `Request` model) - `sql/01_schema.sql`

### `POST /api/v1/deploy/requests/{requestId}/responses`
-   **Handler**: `respond_to_request_endpoint` in `server/api/routers/requests.py`
-   **Query**: `request_service.respond_to_request()` -> `request_repo.update()`
-   **DB Objects**:
    -   `TABLE`: `ops.requests` (from `Request` model) - `sql/01_schema.sql`

---

## 9. Sample Endpoints

### `GET /api/v1/drivers/{driver_id}/active-assignments-sample`
-   **Handler**: `list_driver_active_assignments_sample` in `server/api/routers/role_samples.py`
-   **Query**: No database access.
-   **DB Objects**: None

### `GET /api/v1/owners/{owner_id}/cranes-summary-sample`
-   **Handler**: `list_owner_cranes_summary_sample` in `server/api/routers/role_samples.py`
-   **Query**: No database access.
-   **DB Objects**: None

### `GET /api/v1/sites-sample`
-   **Handler**: `list_managed_sites_sample` in `server/api/routers/role_samples.py`
-   **Query**: No database access.
-   **DB Objects**: None
