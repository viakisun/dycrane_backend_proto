-- Truncate all business tables in ops schema (safe reset for tests)
-- Requires: PostgreSQL, existing ops schema & tables


BEGIN;
SET search_path TO ops, public;


TRUNCATE TABLE
driver_document_items,
driver_document_requests,
driver_attendance,
driver_assignments,
site_crane_assignments,
cranes,
user_orgs,
sites,
orgs,
users
RESTART IDENTITY CASCADE;


COMMIT;