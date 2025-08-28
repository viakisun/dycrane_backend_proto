#!/usr/bin/env python3
"""
DY Crane Safety Management System - End-to-End Test Suite
=========================================================

Validates the complete business workflow:
1. Site creation (SAFETY_MANAGER) → 2. Site approval (MANUFACTURER)
3. Crane listing → 4. Crane assignment → 5. Driver assignment  
6. Attendance recording → 7. Document request → 8. Document submission → 9. Document review

Requirements: PostgreSQL database with ops schema initialized
Run: python test.py or pytest -v test.py
"""

import os
import sys
import uuid
import datetime as dt
import traceback
from typing import Optional, List, Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session

# Import application components
try:
    from app import (
        app, engine, SessionLocal,
        User, UserRole, Org, OrgType, Crane, CraneStatus,
        Site, SiteStatus, SiteCraneAssignment, AssignmentStatus
    )
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    print("Ensure app.py is present with required models")
    sys.exit(1)


class TestData:
    """Container for test data and configuration"""
    
    def __init__(self):
        # Test timing - use future dates to avoid conflicts
        self.days_offset = 45  # Start test period this many days in future
        self.duration_days = 14  # Test period duration
        
        # Calculated dates
        today = dt.date.today()
        self.start_date = today + dt.timedelta(days=self.days_offset)
        self.end_date = self.start_date + dt.timedelta(days=self.duration_days)
        
        # User data - will be populated from database
        self.users = {}
        self.orgs = {}
        self.crane = None
        
        # Test execution data
        self.site_id = None
        self.assignment_ids = {}
        

class DatabaseValidator:
    """Validates database state and finds required test entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_database_ready(self) -> bool:
        """Verify database has required tables and seed data"""
        try:
            # Check basic table access by querying user count
            user_count = self.db.execute(select(func.count(User.id))).scalar()
            if user_count == 0:
                print("ERROR: No users found in database")
                return False
            
            # Check for required user roles
            required_roles = [UserRole.SAFETY_MANAGER, UserRole.MANUFACTURER, UserRole.DRIVER]
            for role in required_roles:
                result = self.db.execute(
                    select(User).where(User.role == role, User.is_active == True).limit(1)
                )
                user = result.scalars().first()
                
                if not user:
                    print(f"ERROR: No active {role.value} found in database")
                    return False
            
            # Check for organizations
            result = self.db.execute(
                select(Org).where(Org.type == OrgType.OWNER).limit(1)
            )
            owner_org = result.scalars().first()
            
            if not owner_org:
                print("ERROR: No OWNER organization found")
                return False
                
            # Check for cranes
            crane_count = self.db.execute(select(func.count(Crane.id))).scalar()
            if crane_count == 0:
                print("ERROR: No cranes found in database")
                return False
                
            print(f"Database contains: {user_count} users, at least 1 owner org, {crane_count} cranes")
            return True
            
        except Exception as e:
            print(f"DATABASE CHECK FAILED: {e}")
            print("This usually means:")
            print("  1. Database connection failed")
            print("  2. Schema 'ops' doesn't exist") 
            print("  3. Tables haven't been created")
            print("  4. Seed data is missing")
            return False
    
    def get_user_by_role(self, role: UserRole) -> User:
        """Get first active user with specified role"""
        result = self.db.execute(
            select(User).where(
                User.role == role,
                User.is_active == True
            ).limit(1)
        )
        user = result.scalars().first()
        
        if not user:
            raise ValueError(f"No active {role.value} user found")
        return user
    
    def find_available_crane(self, start_date: dt.date, end_date: dt.date) -> tuple[Org, Crane]:
        """Find an available NORMAL crane with its owner organization"""
        # Get owner orgs with NORMAL cranes
        result = self.db.execute(
            select(Crane, Org)
            .join(Org, Crane.owner_org_id == Org.id)
            .where(
                Org.type == OrgType.OWNER,
                Crane.status == CraneStatus.NORMAL
            )
        )
        crane_data = result.all()
        
        # Find first crane without conflicting assignments
        for row in crane_data:
            crane, owner = row[0], row[1]
            
            conflicts_result = self.db.execute(
                select(SiteCraneAssignment).where(
                    SiteCraneAssignment.crane_id == crane.id,
                    SiteCraneAssignment.status == AssignmentStatus.ASSIGNED,
                    SiteCraneAssignment.start_date <= end_date,
                    or_(
                        SiteCraneAssignment.end_date == None,
                        SiteCraneAssignment.end_date >= start_date
                    )
                )
            )
            conflicts = conflicts_result.scalars().first()
            
            if not conflicts:
                return owner, crane
                
        raise ValueError(f"No available cranes for period {start_date} to {end_date}")


class APITestClient:
    """Wrapper for FastAPI test client with logging and validation"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.step_counter = 0
    
    def request(self, method: str, url: str, json_data: dict = None, **kwargs) -> dict:
        """Make API request with logging and validation"""
        self.step_counter += 1
        
        print(f"\n[{self.step_counter}] {method.upper()} {url}")
        if json_data:
            print(f"    Request: {self._format_json(json_data)}")
        
        # Make request
        response = self.client.request(method, url, json=json_data, **kwargs)
        
        # Log response
        status_indicator = "✓" if response.status_code < 400 else "✗"
        print(f"    {status_indicator} Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"    Response: {self._format_json(response_data)}")
        except Exception:
            print(f"    Response: {response.text[:100]}...")
        
        # Validate status
        if response.status_code >= 400:
            try:
                error_detail = response.json()
                raise AssertionError(f"API request failed: {error_detail}")
            except:
                raise AssertionError(f"API request failed: HTTP {response.status_code}")
        
        return response.json()
    
    def _format_json(self, data: Any, max_len: int = 120) -> str:
        """Format JSON data for logging"""
        import json
        try:
            formatted = json.dumps(data, default=str, separators=(',', ':'))
            return formatted[:max_len] + ("..." if len(formatted) > max_len else "")
        except:
            return str(data)[:max_len]


class CraneSystemTest:
    """Main test orchestrator"""
    
    def __init__(self):
        self.test_data = TestData()
        self.db_validator = None
        self.api = APITestClient()
        
    def setup(self) -> bool:
        """Initialize test environment and validate prerequisites"""
        print("CRANE SAFETY MANAGEMENT SYSTEM - TEST SUITE")
        print("=" * 60)
        print(f"Test period: {self.test_data.start_date} → {self.test_data.end_date}")
        
        # Database validation
        print("\nValidating database...")
        with SessionLocal() as db:
            self.db_validator = DatabaseValidator(db)
            
            if not self.db_validator.check_database_ready():
                print("\nTEST SETUP FAILED: Database validation failed")
                print("Required actions:")
                print("  1. Run: ./dev.ps1 db:reset")
                print("  2. Ensure PostgreSQL is running")
                print("  3. Check DATABASE_URL environment variable")
                return False
            
            # Load test entities
            try:
                print("Loading required test entities...")
                
                # Load users with detailed error checking
                safety_manager = self.db_validator.get_user_by_role(UserRole.SAFETY_MANAGER)
                print(f"  Found SAFETY_MANAGER: {getattr(safety_manager, 'name', 'NO_NAME')} (ID: {getattr(safety_manager, 'id', 'NO_ID')})")
                
                manufacturer = self.db_validator.get_user_by_role(UserRole.MANUFACTURER)
                print(f"  Found MANUFACTURER: {getattr(manufacturer, 'name', 'NO_NAME')} (ID: {getattr(manufacturer, 'id', 'NO_ID')})")
                
                driver = self.db_validator.get_user_by_role(UserRole.DRIVER)
                print(f"  Found DRIVER: {getattr(driver, 'name', 'NO_NAME')} (ID: {getattr(driver, 'id', 'NO_ID')})")
                
                # Store users
                self.test_data.users['safety_manager'] = safety_manager
                self.test_data.users['manufacturer'] = manufacturer
                self.test_data.users['driver'] = driver
                
                # Load crane and owner org
                owner_org, crane = self.db_validator.find_available_crane(
                    self.test_data.start_date, 
                    self.test_data.end_date
                )
                
                print(f"  Found OWNER organization: {getattr(owner_org, 'name', 'NO_NAME')} (ID: {getattr(owner_org, 'id', 'NO_ID')})")
                print(f"  Found available crane: {getattr(crane, 'model_name', 'NO_MODEL')} (ID: {getattr(crane, 'id', 'NO_ID')})")
                
                self.test_data.orgs['owner'] = owner_org
                self.test_data.crane = crane
                
                print("✓ All test entities loaded successfully")
                return True
                
            except AttributeError as e:
                print(f"\nTEST SETUP FAILED: Database model attribute error")
                print(f"Error details: {e}")
                print("This indicates a mismatch between SQLAlchemy models and database schema")
                print("Possible causes:")
                print("  1. Column names in database don't match model attributes")
                print("  2. Database schema not properly initialized")
                print("  3. Search path not set to 'ops' schema")
                return False
                
            except Exception as e:
                print(f"\nTEST SETUP FAILED: Unable to load required test entities")
                print(f"Error details: {e}")
                print(f"Error type: {type(e).__name__}")
                print("This usually means seed data is incomplete or invalid")
                return False
    
    def run_workflow(self) -> bool:
        """Execute the complete business workflow"""
        print("\nExecuting business workflow...")
        print("-" * 40)
        
        try:
            # Step 1: Create site
            print("STEP 1: Creating construction site...")
            site_data = {
                "name": f"TestSite-{uuid.uuid4().hex[:8]}",
                "address": "Test Construction Address",
                "start_date": str(self.test_data.start_date),
                "end_date": str(self.test_data.end_date),
                "requested_by_id": self.test_data.users['safety_manager'].id
            }
            
            site_response = self.api.request("POST", "/api/sites", site_data)
            self.test_data.site_id = site_response['id']
            assert site_response['status'] == 'PENDING_APPROVAL'
            print(f"  Site created: {site_response['name']} (ID: {site_response['id'][:8]}...)")
            print(f"  Status: {site_response['status']}")
            
            # Step 2: Approve site
            print("\nSTEP 2: Approving site by manufacturer...")
            approval_data = {
                "approved_by_id": self.test_data.users['manufacturer'].id
            }
            
            approval_response = self.api.request(
                "POST", f"/api/sites/{self.test_data.site_id}/approve", approval_data
            )
            assert approval_response['status'] == 'ACTIVE'
            print(f"  Site approved by: {self.test_data.users['manufacturer'].name}")
            print(f"  New status: {approval_response['status']}")
            
            # Step 3: List owner's cranes
            print("\nSTEP 3: Listing available cranes...")
            cranes_response = self.api.request(
                "GET", f"/api/owners/{self.test_data.orgs['owner'].id}/cranes"
            )
            assert len(cranes_response) > 0
            print(f"  Found {len(cranes_response)} cranes owned by {self.test_data.orgs['owner'].name}")
            for crane in cranes_response:
                print(f"    - {crane['model_name']} ({crane['status']}) ID: {crane['id'][:8]}...")
            
            # Step 4: Assign crane to site
            print("\nSTEP 4: Assigning crane to construction site...")
            crane_assignment_data = {
                "site_id": self.test_data.site_id,
                "crane_id": self.test_data.crane.id,
                "safety_manager_id": self.test_data.users['safety_manager'].id,
                "start_date": str(self.test_data.start_date),
                "end_date": str(self.test_data.end_date - dt.timedelta(days=1))
            }
            
            crane_assign_response = self.api.request(
                "POST", "/api/assignments/crane", crane_assignment_data
            )
            self.test_data.assignment_ids['site_crane'] = crane_assign_response['assignment_id']
            print(f"  Crane {self.test_data.crane.model_name} assigned to site")
            print(f"  Assignment period: {crane_assignment_data['start_date']} to {crane_assignment_data['end_date']}")
            print(f"  Assignment ID: {crane_assign_response['assignment_id'][:8]}...")
            
            # Step 5: Assign driver
            print("\nSTEP 5: Assigning driver to crane...")
            driver_assignment_data = {
                "site_crane_id": self.test_data.assignment_ids['site_crane'],
                "driver_id": self.test_data.users['driver'].id,
                "start_date": str(self.test_data.start_date + dt.timedelta(days=1)),
                "end_date": str(self.test_data.end_date - dt.timedelta(days=2))
            }
            
            driver_assign_response = self.api.request(
                "POST", "/api/assignments/driver", driver_assignment_data
            )
            self.test_data.assignment_ids['driver'] = driver_assign_response['driver_assignment_id']
            print(f"  Driver {self.test_data.users['driver'].name} assigned to crane")
            print(f"  Work period: {driver_assignment_data['start_date']} to {driver_assignment_data['end_date']}")
            print(f"  Driver assignment ID: {driver_assign_response['driver_assignment_id'][:8]}...")
            
            # Step 6: Record attendance
            print("\nSTEP 6: Recording driver attendance...")
            work_date = self.test_data.start_date + dt.timedelta(days=3)
            check_in = dt.datetime.combine(work_date, dt.time(8, 30))
            check_out = dt.datetime.combine(work_date, dt.time(17, 45))
            
            attendance_data = {
                "driver_assignment_id": self.test_data.assignment_ids['driver'],
                "work_date": str(work_date),
                "check_in_at": check_in.isoformat(),
                "check_out_at": check_out.isoformat()
            }
            
            attendance_response = self.api.request("POST", "/api/attendance", attendance_data)
            print(f"  Attendance recorded for: {work_date}")
            print(f"  Check-in: {check_in.strftime('%H:%M')}, Check-out: {check_out.strftime('%H:%M')}")
            print(f"  Work hours: {(check_out - check_in).total_seconds() / 3600:.1f} hours")
            
            # Step 7: Create document request
            print("\nSTEP 7: Creating document request...")
            doc_request_data = {
                "site_id": self.test_data.site_id,
                "driver_id": self.test_data.users['driver'].id,
                "requested_by_id": self.test_data.users['safety_manager'].id,
                "due_date": str(self.test_data.end_date - dt.timedelta(days=3))
            }
            
            doc_request_response = self.api.request(
                "POST", "/api/docs/requests", doc_request_data
            )
            request_id = doc_request_response['request_id']
            print(f"  Document request created for driver: {self.test_data.users['driver'].name}")
            print(f"  Due date: {doc_request_data['due_date']}")
            print(f"  Request ID: {request_id[:8]}...")
            
            # Step 8: Submit document
            print("\nSTEP 8: Submitting safety document...")
            doc_submission_data = {
                "request_id": request_id,
                "doc_type": "SafetyCertification",
                "file_url": "https://s3.ap-northeast-2.amazonaws.com/crane-docs/safety/cert-2025.pdf"
            }
            
            doc_submit_response = self.api.request(
                "POST", "/api/docs/items/submit", doc_submission_data
            )
            item_id = doc_submit_response['item_id']
            print(f"  Document submitted: {doc_submission_data['doc_type']}")
            print(f"  File URL: {doc_submission_data['file_url']}")
            print(f"  Document item ID: {item_id[:8]}...")
            
            # Step 9: Review document
            print("\nSTEP 9: Reviewing and approving document...")
            review_data = {
                "item_id": item_id,
                "reviewer_id": self.test_data.users['safety_manager'].id,
                "approve": True
            }
            
            review_response = self.api.request(
                "POST", "/api/docs/items/review", review_data
            )
            assert review_response['status'] == 'APPROVED'
            print(f"  Document reviewed by: {self.test_data.users['safety_manager'].name}")
            print(f"  Review result: {review_response['status']}")
            
            print("\n" + "=" * 60)
            print("WORKFLOW COMPLETED SUCCESSFULLY")
            print(f"All {self.api.step_counter} API calls executed successfully")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\nWORKFLOW EXECUTION FAILED AT STEP {self.api.step_counter}")
            print(f"Error: {e}")
            print("This indicates an API endpoint error or business logic validation failure")
            traceback.print_exc()
            return False


# Test functions for pytest compatibility
def test_database_connection():
    """Test database connectivity"""
    with SessionLocal() as db:
        result = db.execute(select(func.count(User.id))).scalar()
        assert result >= 0, "Database connection failed"


def test_complete_workflow():
    """Main test - complete business workflow"""
    test_system = CraneSystemTest()
    
    setup_success = test_system.setup()
    if not setup_success:
        pytest.fail("Test environment setup failed - database or seed data issues")
    
    workflow_success = test_system.run_workflow()
    if not workflow_success:
        pytest.fail("Business workflow execution failed - API or business logic error")


# Direct execution support
def main():
    """Run tests directly"""
    try:
        test_system = CraneSystemTest()
        
        if not test_system.setup():
            print("\nEXIT: Test environment setup failed")
            sys.exit(1)
            
        if not test_system.run_workflow():
            print("\nEXIT: Business workflow test failed") 
            sys.exit(1)
            
        print("\n" + "=" * 60)
        print("SUCCESS: All tests passed - System is working correctly!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nEXIT: Test interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\nCRITICAL ERROR: Unexpected test framework failure")
        print(f"Error details: {e}")
        print("This indicates a problem with the test code itself, not the system being tested")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()