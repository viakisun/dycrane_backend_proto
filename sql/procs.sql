-- =========================================================
-- DY Crane Safety Management - Domain Logic Stored Procedures
-- Moves core business validation and operations from app.py to database
-- All procedures maintain API contract compatibility
-- =========================================================

SET search_path TO ops, public;

-- =========================================================
-- HELPER FUNCTIONS
-- =========================================================

-- Validate user exists, is active, and has expected role
CREATE OR REPLACE FUNCTION ops.fn_validate_user_role(
    p_user_id TEXT,
    p_expected_role ops.user_role
) RETURNS ops.users AS $$
DECLARE
    v_user ops.users;
BEGIN
    SELECT * INTO v_user FROM ops.users WHERE id = p_user_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User % not found', p_user_id;
    END IF;
    
    IF NOT v_user.is_active THEN
        RAISE EXCEPTION 'User % is inactive', p_user_id;
    END IF;
    
    IF v_user.role != p_expected_role THEN
        RAISE EXCEPTION 'User must have role %, but has %', p_expected_role, v_user.role;
    END IF;
    
    RETURN v_user;
END;
$$ LANGUAGE plpgsql;

-- Check if crane is available for assignment period
CREATE OR REPLACE FUNCTION ops.fn_is_crane_available(
    p_crane_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS BOOLEAN AS $$
DECLARE
    v_crane ops.cranes;
    v_conflict_count INTEGER;
BEGIN
    -- Check crane exists and has NORMAL status
    SELECT * INTO v_crane FROM ops.cranes WHERE id = p_crane_id;
    
    IF NOT FOUND OR v_crane.status != 'NORMAL' THEN
        RETURN FALSE;
    END IF;
    
    -- Check for overlapping assignments
    SELECT COUNT(*) INTO v_conflict_count
    FROM ops.site_crane_assignments
    WHERE crane_id = p_crane_id
      AND status = 'ASSIGNED'
      AND start_date <= COALESCE(p_end_date, '9999-12-31'::DATE)
      AND COALESCE(end_date, '9999-12-31'::DATE) >= p_start_date;
    
    RETURN v_conflict_count = 0;
END;
$$ LANGUAGE plpgsql;

-- Validate assignment dates are within site period
CREATE OR REPLACE FUNCTION ops.fn_validate_assignment_within_site(
    p_site_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS VOID AS $$
DECLARE
    v_site ops.sites;
BEGIN
    SELECT * INTO v_site FROM ops.sites WHERE id = p_site_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Site not found';
    END IF;
    
    IF p_start_date < v_site.start_date THEN
        RAISE EXCEPTION 'Assignment start_date % is before site start_date %', 
            p_start_date, v_site.start_date;
    END IF;
    
    IF p_end_date IS NOT NULL AND p_end_date > v_site.end_date THEN
        RAISE EXCEPTION 'Assignment end_date % is after site end_date %',
            p_end_date, v_site.end_date;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- CORE BUSINESS OPERATIONS
-- =========================================================

-- Create a new construction site
CREATE OR REPLACE FUNCTION ops.sp_site_create(
    p_name TEXT,
    p_address TEXT,
    p_start_date DATE,
    p_end_date DATE,
    p_requested_by_id TEXT
) RETURNS ops.sites AS $$
DECLARE
    v_site ops.sites;
    v_site_id TEXT;
BEGIN
    -- Validate safety manager
    PERFORM ops.fn_validate_user_role(p_requested_by_id, 'SAFETY_MANAGER');
    
    -- Validate date range
    IF p_end_date < p_start_date THEN
        RAISE EXCEPTION 'end_date must be after start_date';
    END IF;
    
    -- Generate ID and create site
    v_site_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.sites (
        id, name, address, start_date, end_date, 
        status, requested_by_id, requested_at
    ) VALUES (
        v_site_id, p_name, p_address, p_start_date, p_end_date,
        'PENDING_APPROVAL', p_requested_by_id, now()
    ) RETURNING * INTO v_site;
    
    RETURN v_site;
END;
$$ LANGUAGE plpgsql;

-- Approve a site (manufacturer only)
CREATE OR REPLACE FUNCTION ops.sp_site_approve(
    p_site_id TEXT,
    p_approved_by_id TEXT
) RETURNS ops.sites AS $$
DECLARE
    v_site ops.sites;
    v_approver ops.users;
BEGIN
    -- Validate manufacturer
    v_approver := ops.fn_validate_user_role(p_approved_by_id, 'MANUFACTURER');
    
    -- Get and validate site
    SELECT * INTO v_site FROM ops.sites WHERE id = p_site_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Site not found';
    END IF;
    
    IF v_site.status != 'PENDING_APPROVAL' THEN
        RAISE EXCEPTION 'Site status is %, cannot approve', v_site.status;
    END IF;
    
    -- Update site status
    UPDATE ops.sites 
    SET status = 'ACTIVE',
        approved_by_id = p_approved_by_id,
        approved_at = now()
    WHERE id = p_site_id
    RETURNING * INTO v_site;
    
    RETURN v_site;
END;
$$ LANGUAGE plpgsql;

-- Assign crane to site
CREATE OR REPLACE FUNCTION ops.sp_assign_crane(
    p_site_id TEXT,
    p_crane_id TEXT,
    p_safety_manager_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS TEXT AS $$
DECLARE
    v_assignment_id TEXT;
    v_site ops.sites;
BEGIN
    -- Validate safety manager
    PERFORM ops.fn_validate_user_role(p_safety_manager_id, 'SAFETY_MANAGER');
    
    -- Validate site exists and is active
    SELECT * INTO v_site FROM ops.sites WHERE id = p_site_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Site not found';
    END IF;
    
    IF v_site.status != 'ACTIVE' THEN
        RAISE EXCEPTION 'Site status is %, must be ACTIVE to assign cranes', v_site.status;
    END IF;
    
    -- Validate assignment period is within site period
    PERFORM ops.fn_validate_assignment_within_site(p_site_id, p_start_date, p_end_date);
    
    -- Validate crane availability
    IF NOT ops.fn_is_crane_available(p_crane_id, p_start_date, p_end_date) THEN
        RAISE EXCEPTION 'Crane is not available for the specified period (status not NORMAL or conflicting assignment)';
    END IF;
    
    -- Create assignment
    v_assignment_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.site_crane_assignments (
        id, site_id, crane_id, assigned_by, start_date, end_date, status
    ) VALUES (
        v_assignment_id, p_site_id, p_crane_id, p_safety_manager_id,
        p_start_date, p_end_date, 'ASSIGNED'
    );
    
    RETURN v_assignment_id;
END;
$$ LANGUAGE plpgsql;

-- Assign driver to site-crane
CREATE OR REPLACE FUNCTION ops.sp_assign_driver(
    p_site_crane_id TEXT,
    p_driver_id TEXT,
    p_start_date DATE,
    p_end_date DATE
) RETURNS TEXT AS $$
DECLARE
    v_assignment_id TEXT;
    v_site_crane ops.site_crane_assignments;
BEGIN
    -- Validate driver
    PERFORM ops.fn_validate_user_role(p_driver_id, 'DRIVER');
    
    -- Get site-crane assignment
    SELECT * INTO v_site_crane FROM ops.site_crane_assignments WHERE id = p_site_crane_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Site-crane assignment not found';
    END IF;
    
    -- Validate driver assignment period is within site-crane period
    IF p_start_date < v_site_crane.start_date THEN
        RAISE EXCEPTION 'Driver assignment start_date % is before site-crane start_date %',
            p_start_date, v_site_crane.start_date;
    END IF;
    
    IF p_end_date IS NOT NULL AND v_site_crane.end_date IS NOT NULL AND 
       p_end_date > v_site_crane.end_date THEN
        RAISE EXCEPTION 'Driver assignment end_date % is after site-crane end_date %',
            p_end_date, v_site_crane.end_date;
    END IF;
    
    -- Create driver assignment
    v_assignment_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.driver_assignments (
        id, site_crane_id, driver_id, start_date, end_date, status
    ) VALUES (
        v_assignment_id, p_site_crane_id, p_driver_id, p_start_date, p_end_date, 'ASSIGNED'
    );
    
    RETURN v_assignment_id;
END;
$$ LANGUAGE plpgsql;

-- Record driver attendance
CREATE OR REPLACE FUNCTION ops.sp_record_attendance(
    p_driver_assignment_id TEXT,
    p_work_date DATE,
    p_check_in_at TIMESTAMPTZ,
    p_check_out_at TIMESTAMPTZ
) RETURNS TEXT AS $$
DECLARE
    v_attendance_id TEXT;
    v_assignment ops.driver_assignments;
    v_existing_count INTEGER;
BEGIN
    -- Validate time range
    IF p_check_out_at IS NOT NULL AND p_check_out_at < p_check_in_at THEN
        RAISE EXCEPTION 'check_out_at must be after check_in_at';
    END IF;
    
    -- Get driver assignment
    SELECT * INTO v_assignment FROM ops.driver_assignments WHERE id = p_driver_assignment_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Driver assignment not found';
    END IF;
    
    -- Validate work date is within assignment period
    IF p_work_date < v_assignment.start_date THEN
        RAISE EXCEPTION 'Work date % is before assignment start_date %',
            p_work_date, v_assignment.start_date;
    END IF;
    
    IF v_assignment.end_date IS NOT NULL AND p_work_date > v_assignment.end_date THEN
        RAISE EXCEPTION 'Work date % is after assignment end_date %',
            p_work_date, v_assignment.end_date;
    END IF;
    
    -- Check for duplicate attendance
    SELECT COUNT(*) INTO v_existing_count
    FROM ops.driver_attendance
    WHERE driver_assignment_id = p_driver_assignment_id
      AND work_date = p_work_date;
    
    IF v_existing_count > 0 THEN
        RAISE EXCEPTION 'Attendance already recorded for %', p_work_date;
    END IF;
    
    -- Create attendance record
    v_attendance_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.driver_attendance (
        id, driver_assignment_id, work_date, check_in_at, check_out_at
    ) VALUES (
        v_attendance_id, p_driver_assignment_id, p_work_date, p_check_in_at, p_check_out_at
    );
    
    RETURN v_attendance_id;
END;
$$ LANGUAGE plpgsql;

-- Create document request
CREATE OR REPLACE FUNCTION ops.sp_doc_request_create(
    p_site_id TEXT,
    p_driver_id TEXT,
    p_requested_by_id TEXT,
    p_due_date DATE
) RETURNS TEXT AS $$
DECLARE
    v_request_id TEXT;
    v_site ops.sites;
BEGIN
    -- Validate safety manager
    PERFORM ops.fn_validate_user_role(p_requested_by_id, 'SAFETY_MANAGER');
    
    -- Validate driver
    PERFORM ops.fn_validate_user_role(p_driver_id, 'DRIVER');
    
    -- Validate site exists
    SELECT * INTO v_site FROM ops.sites WHERE id = p_site_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Site not found';
    END IF;
    
    -- Create document request
    v_request_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.driver_document_requests (
        id, site_id, driver_id, requested_by_id, due_date
    ) VALUES (
        v_request_id, p_site_id, p_driver_id, p_requested_by_id, p_due_date
    );
    
    RETURN v_request_id;
END;
$$ LANGUAGE plpgsql;

-- Submit document item
CREATE OR REPLACE FUNCTION ops.sp_doc_item_submit(
    p_request_id TEXT,
    p_doc_type TEXT,
    p_file_url TEXT
) RETURNS TEXT AS $$
DECLARE
    v_item_id TEXT;
    v_request ops.driver_document_requests;
BEGIN
    -- Validate request exists
    SELECT * INTO v_request FROM ops.driver_document_requests WHERE id = p_request_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Document request not found';
    END IF;
    
    -- Create document item
    v_item_id := uuid_generate_v4()::TEXT;
    
    INSERT INTO ops.driver_document_items (
        id, request_id, doc_type, file_url, status, submitted_at
    ) VALUES (
        v_item_id, p_request_id, p_doc_type, p_file_url, 'SUBMITTED', now()
    );
    
    RETURN v_item_id;
END;
$$ LANGUAGE plpgsql;

-- Review document item
CREATE OR REPLACE FUNCTION ops.sp_doc_item_review(
    p_item_id TEXT,
    p_reviewer_id TEXT,
    p_approve BOOLEAN
) RETURNS ops.doc_item_status AS $$
DECLARE
    v_item ops.driver_document_items;
    v_new_status ops.doc_item_status;
BEGIN
    -- Validate reviewer is safety manager
    PERFORM ops.fn_validate_user_role(p_reviewer_id, 'SAFETY_MANAGER');
    
    -- Get document item
    SELECT * INTO v_item FROM ops.driver_document_items WHERE id = p_item_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Document item not found';
    END IF;
    
    IF v_item.status NOT IN ('SUBMITTED', 'PENDING') THEN
        RAISE EXCEPTION 'Document item status is %, cannot review', v_item.status;
    END IF;
    
    -- Determine new status
    v_new_status := CASE WHEN p_approve THEN 'APPROVED'::ops.doc_item_status 
                         ELSE 'REJECTED'::ops.doc_item_status END;
    
    -- Update item
    UPDATE ops.driver_document_items 
    SET reviewer_id = p_reviewer_id,
        status = v_new_status,
        reviewed_at = now()
    WHERE id = p_item_id;
    
    RETURN v_new_status;
END;
$$ LANGUAGE plpgsql;

-- =========================================================
-- QUERY HELPER FUNCTIONS
-- =========================================================

-- Get cranes owned by organization (JSON format for API)
CREATE OR REPLACE FUNCTION ops.fn_owner_cranes_json(p_owner_org_id TEXT)
RETURNS JSON AS $$
DECLARE
    v_org ops.orgs;
BEGIN
    -- Validate org exists and is OWNER type
    SELECT * INTO v_org FROM ops.orgs WHERE id = p_owner_org_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Organization not found';
    END IF;
    
    IF v_org.type != 'OWNER' THEN
        RAISE EXCEPTION 'Organization is not an owner type';
    END IF;
    
    -- Return cranes as JSON array
    RETURN (
        SELECT COALESCE(json_agg(row_to_json(t)), '[]'::json)
        FROM (
            SELECT id, owner_org_id, model_name, serial_no, status, created_at, updated_at
            FROM ops.cranes 
            WHERE owner_org_id = p_owner_org_id 
            ORDER BY model_name
        ) t
    );
END;
$$ LANGUAGE plpgsql;