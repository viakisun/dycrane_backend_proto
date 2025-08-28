"""
API routes for DY Crane Safety Management System.
Defines all REST endpoints with proper documentation and error handling.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db, db_manager
from schemas import (
    SiteCreate, SiteOut, SiteApprove, CraneOut, AssignCraneIn, AssignDriverIn,
    AttendanceIn, DocRequestIn, DocItemSubmitIn, DocItemReviewIn,
    AssignmentResponse, DriverAssignmentResponse, AttendanceResponse,
    DocRequestResponse, DocSubmitResponse, DocItemResponse, HealthCheckResponse
)
from models import Site
from services import StoredProcedureService, ValidationService, CraneService
import datetime as dt

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api", tags=["Crane Safety Management"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for service monitoring.
    
    Returns:
        HealthCheckResponse: Service status and database connectivity
    """
    logger.debug("Health check requested")
    
    database_healthy = db_manager.health_check()
    
    response = HealthCheckResponse(
        status="healthy" if database_healthy else "degraded",
        timestamp=dt.datetime.utcnow(),
        database_healthy=database_healthy
    )
    
    if not database_healthy:
        logger.warning("Health check shows database connectivity issues")
    else:
        logger.debug("Health check passed")
    
    return response


# ========= SITE MANAGEMENT =========

@router.post("/sites", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreate, db: Session = Depends(get_db)):
    """
    Create a new construction site.
    
    Requires SAFETY_MANAGER role for the requesting user.
    Site will be created with PENDING_APPROVAL status.
    
    Args:
        payload: Site creation data including name, dates, and requesting user
        
    Returns:
        SiteOut: Created site information
        
    Raises:
        HTTPException: 
            - 403 if user lacks SAFETY_MANAGER role
            - 400 if validation fails (e.g., invalid date range)
    """
    logger.info(f"Creating site: {payload.name} (requested by: {payload.requested_by_id})")
    
    site = StoredProcedureService.execute_returning_row(
        db, 
        "ops.sp_site_create",
        {
            "p_name": payload.name,
            "p_address": payload.address,
            "p_start_date": payload.start_date,
            "p_end_date": payload.end_date,
            "p_requested_by_id": payload.requested_by_id
        },
        Site
    )
    
    db.commit()
    logger.info(f"Site created successfully: {site.id} - {site.name}")
    return site


@router.post("/sites/{site_id}/approve", response_model=SiteOut)
def approve_site(site_id: str, payload: SiteApprove, db: Session = Depends(get_db)):
    """
    Approve a construction site.
    
    Only users with MANUFACTURER role can approve sites.
    Updates site status from PENDING_APPROVAL to ACTIVE.
    
    Args:
        site_id: ID of the site to approve
        payload: Approval data including approving user ID
        
    Returns:
        SiteOut: Updated site information with approval details
        
    Raises:
        HTTPException:
            - 404 if site not found
            - 403 if user lacks MANUFACTURER role
            - 400 if site not in PENDING_APPROVAL status
    """
    logger.info(f"Approving site {site_id} by user {payload.approved_by_id}")
    
    site = StoredProcedureService.execute_returning_row(
        db,
        "ops.sp_site_approve",
        {
            "p_site_id": site_id,
            "p_approved_by_id": payload.approved_by_id
        },
        Site
    )
    
    db.commit()
    logger.info(f"Site approved successfully: {site.id} - {site.name}")
    return site


# ========= CRANE MANAGEMENT =========

@router.get("/owners/{owner_org_id}/cranes", response_model=List[CraneOut])
def list_owner_cranes(owner_org_id: str, db: Session = Depends(get_db)):
    """
    List all cranes owned by a specific organization.
    
    Returns cranes ordered by model name for consistent presentation.
    Validates that the organization exists and is of OWNER type.
    
    Args:
        owner_org_id: Organization ID to list cranes for
        
    Returns:
        List[CraneOut]: List of cranes owned by the organization
        
    Raises:
        HTTPException:
            - 404 if organization not found
            - 400 if organization is not OWNER type
    """
    logger.info(f"Listing cranes for organization: {owner_org_id}")
    
    cranes = CraneService.list_owner_cranes(db, owner_org_id)
    
    logger.info(f"Found {len(cranes)} cranes for organization: {owner_org_id}")
    return cranes


# ========= ASSIGNMENT MANAGEMENT =========

@router.post("/assignments/crane", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_crane(payload: AssignCraneIn, db: Session = Depends(get_db)):
    """
    Assign a crane to a construction site.
    
    Validates that:
    - Requesting user has SAFETY_MANAGER role
    - Site exists and has ACTIVE status
    - Crane is available and in NORMAL status
    - Assignment period is within site project period
    - No overlapping assignments for the crane
    
    Args:
        payload: Crane assignment data
        
    Returns:
        AssignmentResponse: ID of the created assignment
        
    Raises:
        HTTPException:
            - 404 if site or crane not found
            - 403 if user lacks SAFETY_MANAGER role
            - 400 if site not ACTIVE or validation fails
            - 409 if crane has conflicting assignments
    """
    logger.info(f"Assigning crane {payload.crane_id} to site {payload.site_id}")
    
    assignment_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_assign_crane",
        {
            "p_site_id": payload.site_id,
            "p_crane_id": payload.crane_id,
            "p_safety_manager_id": payload.safety_manager_id,
            "p_start_date": payload.start_date,
            "p_end_date": payload.end_date
        }
    )
    
    db.commit()
    logger.info(f"Crane assignment created: {assignment_id}")
    return AssignmentResponse(assignment_id=assignment_id)


@router.post("/assignments/driver", response_model=DriverAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_driver(payload: AssignDriverIn, db: Session = Depends(get_db)):
    """
    Assign a driver to a site-crane assignment.
    
    Validates that:
    - Target user has DRIVER role
    - Site-crane assignment exists
    - Assignment period is within site-crane assignment period
    - No overlapping driver assignments
    
    Args:
        payload: Driver assignment data
        
    Returns:
        DriverAssignmentResponse: ID of the created driver assignment
        
    Raises:
        HTTPException:
            - 404 if site-crane assignment not found
            - 403 if user lacks DRIVER role
            - 400 if assignment period validation fails
            - 409 if driver has conflicting assignments
    """
    logger.info(f"Assigning driver {payload.driver_id} to site-crane {payload.site_crane_id}")
    
    assignment_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_assign_driver",
        {
            "p_site_crane_id": payload.site_crane_id,
            "p_driver_id": payload.driver_id,
            "p_start_date": payload.start_date,
            "p_end_date": payload.end_date
        }
    )
    
    db.commit()
    logger.info(f"Driver assignment created: {assignment_id}")
    return DriverAssignmentResponse(driver_assignment_id=assignment_id)


# ========= ATTENDANCE MANAGEMENT =========

@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def record_attendance(payload: AttendanceIn, db: Session = Depends(get_db)):
    """
    Record driver attendance for a work day.
    
    Validates that:
    - Driver assignment exists
    - Work date is within assignment period
    - No duplicate attendance for the same date
    - Check-out time is after check-in time (if provided)
    
    Args:
        payload: Attendance data including dates and times
        
    Returns:
        AttendanceResponse: ID of the created attendance record
        
    Raises:
        HTTPException:
            - 404 if driver assignment not found
            - 400 if work date outside assignment period
            - 409 if attendance already recorded for the date
    """
    logger.info(f"Recording attendance for assignment {payload.driver_assignment_id} on {payload.work_date}")
    
    attendance_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_record_attendance",
        {
            "p_driver_assignment_id": payload.driver_assignment_id,
            "p_work_date": payload.work_date,
            "p_check_in_at": payload.check_in_at,
            "p_check_out_at": payload.check_out_at
        }
    )
    
    db.commit()
    logger.info(f"Attendance recorded: {attendance_id}")
    return AttendanceResponse(attendance_id=attendance_id)


# ========= DOCUMENT MANAGEMENT =========

@router.post("/docs/requests", response_model=DocRequestResponse, status_code=status.HTTP_201_CREATED)
def create_document_request(payload: DocRequestIn, db: Session = Depends(get_db)):
    """
    Create a document request for a driver.
    
    Allows safety managers to request specific documents from drivers
    for compliance purposes.
    
    Validates that:
    - Requesting user has SAFETY_MANAGER role
    - Target user has DRIVER role
    - Site exists
    
    Args:
        payload: Document request data
        
    Returns:
        DocRequestResponse: ID of the created document request
        
    Raises:
        HTTPException:
            - 404 if site or driver not found
            - 403 if requester lacks SAFETY_MANAGER role
    """
    logger.info(f"Creating document request for driver {payload.driver_id} on site {payload.site_id}")
    
    request_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_doc_request_create",
        {
            "p_site_id": payload.site_id,
            "p_driver_id": payload.driver_id,
            "p_requested_by_id": payload.requested_by_id,
            "p_due_date": payload.due_date
        }
    )
    
    db.commit()
    logger.info(f"Document request created: {request_id}")
    return DocRequestResponse(request_id=request_id)


@router.post("/docs/items/submit", response_model=DocSubmitResponse, status_code=status.HTTP_201_CREATED)
def submit_document_item(payload: DocItemSubmitIn, db: Session = Depends(get_db)):
    """
    Submit a document item in response to a document request.
    
    Validates file URL security requirements at the application layer
    before processing in the database.
    
    File URL requirements:
    - Must use HTTPS protocol
    - Must have allowed file extension (.pdf, .jpg, .jpeg, .png)
    
    Args:
        payload: Document submission data including file URL
        
    Returns:
        DocSubmitResponse: ID of the created document item
        
    Raises:
        HTTPException:
            - 404 if document request not found
            - 400 if file URL doesn't meet security requirements
    """
    logger.info(f"Submitting document for request {payload.request_id}: {payload.doc_type}")
    
    # Application-layer file URL validation
    ValidationService.validate_file_url(str(payload.file_url))
    
    item_id = StoredProcedureService.execute_returning_id(
        db,
        "ops.sp_doc_item_submit",
        {
            "p_request_id": payload.request_id,
            "p_doc_type": payload.doc_type,
            "p_file_url": str(payload.file_url)
        }
    )
    
    db.commit()
    logger.info(f"Document item submitted: {item_id}")
    return DocSubmitResponse(item_id=item_id)


@router.post("/docs/items/review", response_model=DocItemResponse)
def review_document_item(payload: DocItemReviewIn, db: Session = Depends(get_db)):
    """
    Review a submitted document item (approve or reject).
    
    Only users with SAFETY_MANAGER role can review documents.
    Updates document status and records review timestamp.
    
    Args:
        payload: Review data including approval decision
        
    Returns:
        DocItemResponse: Document item ID and new status
        
    Raises:
        HTTPException:
            - 404 if document item not found
            - 403 if reviewer lacks SAFETY_MANAGER role
            - 400 if document not in reviewable status
    """
    action = "approving" if payload.approve else "rejecting"
    logger.info(f"Reviewing document item {payload.item_id}: {action}")
    
    status_value = StoredProcedureService.execute_returning_status(
        db,
        "ops.sp_doc_item_review",
        {
            "p_item_id": payload.item_id,
            "p_reviewer_id": payload.reviewer_id,
            "p_approve": payload.approve
        }
    )
    
    db.commit()
    logger.info(f"Document review completed: {payload.item_id} -> {status_value}")
    return DocItemResponse(item_id=payload.item_id, status=status_value)