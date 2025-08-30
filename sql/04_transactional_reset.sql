-- Truncate only transactional tables, preserving master data (users, cranes, etc.)
BEGIN;
SET search_path TO ops, public;

TRUNCATE TABLE
sites,
requests,
site_crane_assignments,
driver_assignments,
driver_attendance,
driver_document_requests,
driver_document_items
RESTART IDENTITY CASCADE;

COMMIT;
