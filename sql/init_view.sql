-- =========================================================
-- DY Crane Safety Management - Enhanced Views and Query Functions
-- API-friendly views and aggregation functions
-- =========================================================

SET search_path TO ops, public;

-- =========================================================
-- DROP EXISTING VIEWS (for idempotent updates)
-- =========================================================

DROP VIEW IF EXISTS ops.v_owner_cranes CASCADE;
DROP VIEW IF EXISTS ops.v_site_assignments CASCADE;
DROP VIEW IF EXISTS ops.v_driver_workload CASCADE;
DROP VIEW IF EXISTS ops.available_cranes CASCADE;
DROP VIEW IF EXISTS ops.site_summary CASCADE;
DROP VIEW IF EXISTS ops.driver_activity CASCADE;

-- =========================================================
-- ENHANCED VIEWS
-- =========================================================

-- Available cranes (not currently assigned and in NORMAL status)
-- Enhanced with owner organization details
CREATE VIEW ops.available_cranes AS
SELECT 
    c.id,
    c.owner_org_id,
    cm.model_name,
    c.serial_no,
    c.status,
    c.created_at,
    c.updated_at,
    o.name as owner_name,
    o.type as owner_type
FROM ops.cranes c
JOIN ops.orgs o ON c.owner_org_id = o.id
JOIN ops.crane_models cm ON c.model_id = cm.id
WHERE c.status = 'NORMAL'
  AND NOT EXISTS (
    SELECT 1
    FROM ops.site_crane_assignments sca
    WHERE sca.crane_id = c.id
      AND sca.status = 'ASSIGNED'
      AND sca.start_date <= CURRENT_DATE
      AND COALESCE(sca.end_date, 'infinity'::date) >= CURRENT_DATE
  );

-- Owner cranes view (optimized for API endpoint)
CREATE VIEW ops.v_owner_cranes AS
SELECT 
    c.id,
    c.owner_org_id,
    cm.model_name,
    c.serial_no,
    c.status,
    c.created_at,
    c.updated_at,
    -- Assignment status
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM ops.site_crane_assignments sca 
            WHERE sca.crane_id = c.id 
              AND sca.status = 'ASSIGNED'
              AND sca.start_date <= CURRENT_DATE
              AND COALESCE(sca.end_date, '9999-12-31'::date) >= CURRENT_DATE
        ) THEN 'ASSIGNED'
        ELSE 'AVAILABLE'
    END as assignment_status,
    -- Current assignment details if any
    (
        SELECT json_build_object(
            'site_id', s.id,
            'site_name', s.name,
            'start_date', sca.start_date,
            'end_date', sca.end_date
        )
        FROM ops.site_crane_assignments sca
        JOIN ops.sites s ON sca.site_id = s.id
        WHERE sca.crane_id = c.id 
          AND sca.status = 'ASSIGNED'
          AND sca.start_date <= CURRENT_DATE
          AND COALESCE(sca.end_date, '9999-12-31'::date) >= CURRENT_DATE
        LIMIT 1
    ) as current_assignment
FROM ops.cranes c
JOIN ops.crane_models cm ON c.model_id = cm.id
ORDER BY cm.model_name, c.serial_no;

-- Site assignment summary with enhanced metrics
CREATE VIEW ops.site_summary AS
SELECT
    s.id AS site_id,
    s.name AS site_name,
    s.address,
    s.status AS site_status,
    s.start_date,
    s.end_date,
    s.requested_at,
    s.approved_at,
    -- Requestor and approver details
    req_user.name as requested_by_name,
    req_user.email as requested_by_email,
    app_user.name as approved_by_name,
    app_user.email as approved_by_email,
    -- Assignment counts
    COUNT(sca.id) FILTER (WHERE sca.status = 'ASSIGNED') AS assigned_cranes,
    COUNT(da.id) FILTER (WHERE da.status = 'ASSIGNED') AS assigned_drivers,
    -- Document request counts
    COUNT(ddr.id) AS document_requests,
    COUNT(ddi.id) FILTER (WHERE ddi.status = 'PENDING') AS pending_documents,
    COUNT(ddi.id) FILTER (WHERE ddi.status = 'APPROVED') AS approved_documents,
    -- Timeline metrics
    CASE 
        WHEN s.end_date < CURRENT_DATE THEN 'COMPLETED'
        WHEN s.start_date > CURRENT_DATE THEN 'UPCOMING'
        ELSE 'ACTIVE'
    END as timeline_status,
    s.end_date - s.start_date + 1 as total_project_days,
    GREATEST(0, CURRENT_DATE - s.start_date + 1) as elapsed_days,
    GREATEST(0, s.end_date - CURRENT_DATE + 1) as remaining_days
FROM ops.sites s
LEFT JOIN ops.users req_user ON s.requested_by_id = req_user.id
LEFT JOIN ops.users app_user ON s.approved_by_id = app_user.id
LEFT JOIN ops.site_crane_assignments sca ON s.id = sca.site_id
LEFT JOIN ops.driver_assignments da ON sca.id = da.site_crane_id
LEFT JOIN ops.driver_document_requests ddr ON s.id = ddr.site_id
LEFT JOIN ops.driver_document_items ddi ON ddr.id = ddi.request_id
GROUP BY 
    s.id, s.name, s.address, s.status, s.start_date, s.end_date, 
    s.requested_at, s.approved_at,
    req_user.name, req_user.email, app_user.name, app_user.email;

-- Driver work activity summary with enhanced metrics
CREATE VIEW ops.driver_activity AS
SELECT
    da.id AS assignment_id,
    da.driver_id,
    da.site_crane_id,
    sca.site_id,
    sca.crane_id,
    da.start_date AS assignment_start,
    da.end_date AS assignment_end,
    da.status as assignment_status,
    -- Driver and site details
    u.name as driver_name,
    u.email as driver_email,
    s.name as site_name,
    cm.model_name as crane_model,
    c.serial_no as crane_serial,
    -- Attendance metrics
    COUNT(att.id) AS total_work_days,
    COUNT(att.id) FILTER (WHERE att.check_out_at IS NOT NULL) AS completed_days,
    COUNT(att.id) FILTER (WHERE att.check_out_at IS NULL) AS incomplete_days,
    -- Time metrics
    MIN(att.check_in_at) AS first_check_in,
    MAX(att.check_out_at) AS last_check_out,
    AVG(
        CASE 
            WHEN att.check_out_at IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (att.check_out_at - att.check_in_at)) / 3600 
        END
    ) AS avg_daily_hours,
    SUM(
        CASE 
            WHEN att.check_out_at IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (att.check_out_at - att.check_in_at)) / 3600 
            ELSE 0 
        END
    ) AS total_hours_worked,
    -- Recent activity
    MAX(att.work_date) as last_work_date,
    COUNT(att.id) FILTER (
        WHERE att.work_date >= CURRENT_DATE - INTERVAL '7 days'
    ) as work_days_last_week,
    -- Assignment timeline
    CASE 
        WHEN da.end_date IS NOT NULL AND da.end_date < CURRENT_DATE THEN 'COMPLETED'
        WHEN da.start_date > CURRENT_DATE THEN 'UPCOMING'
        ELSE 'ACTIVE'
    END as timeline_status
FROM ops.driver_assignments da
JOIN ops.site_crane_assignments sca ON da.site_crane_id = sca.id
JOIN ops.sites s ON sca.site_id = s.id
JOIN ops.cranes c ON sca.crane_id = c.id
JOIN ops.crane_models cm ON c.model_id = cm.id
JOIN ops.users u ON da.driver_id = u.id
LEFT JOIN ops.driver_attendance att ON da.id = att.driver_assignment_id
GROUP BY 
    da.id, da.driver_id, da.site_crane_id, sca.site_id, sca.crane_id,
    da.start_date, da.end_date, da.status,
    u.name, u.email, s.name, cm.model_name, c.serial_no;

-- Site assignments with full relationship details
CREATE VIEW ops.v_site_assignments AS
SELECT
    sca.id as assignment_id,
    sca.site_id,
    sca.crane_id,
    sca.start_date,
    sca.end_date,
    sca.status as assignment_status,
    -- Site details
    s.name as site_name,
    s.address as site_address,
    s.status as site_status,
    s.start_date as site_start,
    s.end_date as site_end,
    -- Crane details
    cm.model_name,
    c.serial_no,
    c.status as crane_status,
    o.name as owner_name,
    -- Assigned by details
    u.name as assigned_by_name,
    u.email as assigned_by_email,
    -- Driver assignments count
    COUNT(da.id) FILTER (WHERE da.status = 'ASSIGNED') as assigned_drivers,
    -- Timeline status
    CASE 
        WHEN sca.end_date IS NOT NULL AND sca.end_date < CURRENT_DATE THEN 'COMPLETED'
        WHEN sca.start_date > CURRENT_DATE THEN 'UPCOMING'
        ELSE 'ACTIVE'
    END as timeline_status
FROM ops.site_crane_assignments sca
JOIN ops.sites s ON sca.site_id = s.id
JOIN ops.cranes c ON sca.crane_id = c.id
JOIN ops.crane_models cm ON c.model_id = cm.id
JOIN ops.orgs o ON c.owner_org_id = o.id
JOIN ops.users u ON sca.assigned_by = u.id
LEFT JOIN ops.driver_assignments da ON sca.id = da.site_crane_id
GROUP BY 
    sca.id, sca.site_id, sca.crane_id, sca.start_date, sca.end_date, sca.status,
    s.name, s.address, s.status, s.start_date, s.end_date,
    cm.model_name, c.serial_no, c.status, o.name, u.name, u.email;

-- Driver workload summary
CREATE VIEW ops.v_driver_workload AS
SELECT
    u.id as driver_id,
    u.name as driver_name,
    u.email as driver_email,
    u.is_active,
    -- Current assignments
    COUNT(da.id) FILTER (
        WHERE da.status = 'ASSIGNED' 
          AND da.start_date <= CURRENT_DATE 
          AND COALESCE(da.end_date, '9999-12-31'::date) >= CURRENT_DATE
    ) as current_assignments,
    -- Future assignments
    COUNT(da.id) FILTER (
        WHERE da.status = 'ASSIGNED' 
          AND da.start_date > CURRENT_DATE
    ) as future_assignments,
    -- Total assignments
    COUNT(da.id) as total_assignments,
    -- Recent work activity
    MAX(att.work_date) as last_work_date,
    COUNT(DISTINCT att.work_date) FILTER (
        WHERE att.work_date >= CURRENT_DATE - INTERVAL '30 days'
    ) as work_days_last_month,
    -- Document compliance
    COUNT(ddr.id) as document_requests_received,
    COUNT(ddi.id) FILTER (WHERE ddi.status = 'APPROVED') as documents_approved,
    COUNT(ddi.id) FILTER (WHERE ddi.status = 'PENDING') as documents_pending,
    -- Availability status
    CASE 
        WHEN NOT u.is_active THEN 'INACTIVE'
        WHEN EXISTS (
            SELECT 1 FROM ops.driver_assignments da2 
            WHERE da2.driver_id = u.id 
              AND da2.status = 'ASSIGNED'
              AND da2.start_date <= CURRENT_DATE 
              AND COALESCE(da2.end_date, '9999-12-31'::date) >= CURRENT_DATE
        ) THEN 'ASSIGNED'
        ELSE 'AVAILABLE'
    END as availability_status
FROM ops.users u
LEFT JOIN ops.driver_assignments da ON u.id = da.driver_id
LEFT JOIN ops.driver_attendance att ON da.id = att.driver_assignment_id
LEFT JOIN ops.driver_document_requests ddr ON u.id = ddr.driver_id
LEFT JOIN ops.driver_document_items ddi ON ddr.id = ddi.request_id
WHERE u.role = 'DRIVER'
GROUP BY u.id, u.name, u.email, u.is_active;

-- =========================================================
-- PERFORMANCE INDEXES
-- =========================================================

-- Partial indexes for assigned status (most common queries)
CREATE INDEX IF NOT EXISTS idx_site_crane_assignments_assigned 
ON ops.site_crane_assignments(crane_id, start_date, end_date) 
WHERE status = 'ASSIGNED';

CREATE INDEX IF NOT EXISTS idx_driver_assignments_assigned 
ON ops.driver_assignments(driver_id, start_date, end_date) 
WHERE status = 'ASSIGNED';

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_driver_document_items_request_status 
ON ops.driver_document_items(request_id, status);

CREATE INDEX IF NOT EXISTS idx_driver_attendance_assignment_date 
ON ops.driver_attendance(driver_assignment_id, work_date);

CREATE INDEX IF NOT EXISTS idx_sites_status_dates 
ON ops.sites(status, start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_cranes_owner_status 
ON ops.cranes(owner_org_id, status);

-- Index for timeline queries
CREATE INDEX IF NOT EXISTS idx_assignments_timeline 
ON ops.site_crane_assignments(start_date, end_date, status);

CREATE INDEX IF NOT EXISTS idx_driver_assignments_timeline 
ON ops.driver_assignments(start_date, end_date, status);

-- =========================================================
-- QUERY OPTIMIZATION FUNCTIONS
-- =========================================================

-- Get assignment conflicts for a crane (used in availability checking)
CREATE OR REPLACE FUNCTION ops.fn_get_crane_conflicts(
    p_crane_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS TABLE(
    assignment_id TEXT,
    site_name TEXT,
    start_date DATE,
    end_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sca.id,
        s.name,
        sca.start_date,
        sca.end_date
    FROM ops.site_crane_assignments sca
    JOIN ops.sites s ON sca.site_id = s.id
    WHERE sca.crane_id = p_crane_id
      AND sca.status = 'ASSIGNED'
      AND sca.start_date <= COALESCE(p_end_date, '9999-12-31'::DATE)
      AND COALESCE(sca.end_date, '9999-12-31'::DATE) >= p_start_date;
END;
$$ LANGUAGE plpgsql;

-- Get driver conflicts for assignment period
CREATE OR REPLACE FUNCTION ops.fn_get_driver_conflicts(
    p_driver_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS TABLE(
    assignment_id TEXT,
    site_name TEXT,
    crane_model TEXT,
    start_date DATE,
    end_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        da.id,
        s.name,
        cm.model_name,
        da.start_date,
        da.end_date
    FROM ops.driver_assignments da
    JOIN ops.site_crane_assignments sca ON da.site_crane_id = sca.id
    JOIN ops.sites s ON sca.site_id = s.id
    JOIN ops.cranes c ON sca.crane_id = c.id
    JOIN ops.crane_models cm ON c.model_id = cm.id
    WHERE da.driver_id = p_driver_id
      AND da.status = 'ASSIGNED'
      AND da.start_date <= COALESCE(p_end_date, '9999-12-31'::DATE)
      AND COALESCE(da.end_date, '9999-12-31'::DATE) >= p_start_date;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- VALIDATION
-- =========================================================

DO $$
DECLARE
    view_count INTEGER;
    index_count INTEGER;
BEGIN
    -- Count created views
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views
    WHERE table_schema = 'ops' 
      AND table_name LIKE 'v_%' OR table_name IN ('available_cranes', 'site_summary', 'driver_activity');
    
    -- Count performance indexes  
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'ops'
      AND indexname LIKE 'idx_%_assigned' OR indexname LIKE 'idx_%_timeline';
    
    RAISE NOTICE 'Enhanced views and indexes created:';
    RAISE NOTICE '- Views: %', view_count;
    RAISE NOTICE '- Performance indexes: %', index_count;
    
    IF view_count < 5 THEN
        RAISE WARNING 'Expected at least 5 views, found %', view_count;
    END IF;
    
    RAISE NOTICE 'View layer enhancement complete!';
END;
$$;