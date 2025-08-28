"""
Service layer for DY Crane Safety Management System.
Contains business logic, stored procedure integration, and validation utilities.
"""

import logging
from typing import Any, Dict, Type, TypeVar, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException, status

from config import config
from schemas import DocItemStatus, UserRole, OrgType
from models import Base, Crane, Org

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for SQLAlchemy models
ModelType = TypeVar('ModelType', bound=Base)


class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass


class ValidationError(DatabaseError):
    """Exception for business logic validation failures."""
    pass


class StoredProcedureService:
    """Service for executing stored procedures and handling results."""
    
    @staticmethod
    def execute_returning_row(
        db: Session, 
        sp_name: str, 
        params: Dict[str, Any], 
        model_class: Type[ModelType]
    ) -> ModelType:
        """
        Execute stored procedure and return a single row mapped to SQLAlchemy model.
        
        Args:
            db: Database session
            sp_name: Stored procedure name (e.g., 'ops.sp_site_create')
            params: Parameters dictionary for the stored procedure
            model_class: SQLAlchemy model class to map the result to
            
        Returns:
            Instance of model_class with the returned data
            
        Raises:
            HTTPException: With appropriate status code and error message
        """
        logger.debug(f"Executing stored procedure: {sp_name} with params: {params}")
        
        try:
            # Build parameter placeholders for the stored procedure call
            param_placeholders = ", ".join([f":{key}" for key in params.keys()])
            query = text(f"SELECT * FROM {sp_name}({param_placeholders})")
            
            result = db.execute(query, params)
            row = result.fetchone()
            
            if not row:
                logger.error(f"Stored procedure {sp_name} returned no result")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Stored procedure did not return expected result"
                )
            
            # Convert row to model instance
            model_instance = model_class(**row._asdict())
            logger.info(f"Successfully executed {sp_name}, returned {model_class.__name__} with id: {model_instance.id}")
            return model_instance
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"SQL error in {sp_name}: {e}")
            raise StoredProcedureService._handle_database_error(str(e))
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in {sp_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    def execute_returning_id(db: Session, sp_name: str, params: Dict[str, Any]) -> str:
        """
        Execute stored procedure and return a single ID string.
        
        Args:
            db: Database session
            sp_name: Stored procedure name
            params: Parameters dictionary for the stored procedure
            
        Returns:
            ID string returned by the stored procedure
            
        Raises:
            HTTPException: With appropriate status code and error message
        """
        logger.debug(f"Executing stored procedure for ID: {sp_name} with params: {params}")
        
        try:
            param_placeholders = ", ".join([f":{key}" for key in params.keys()])
            query = text(f"SELECT {sp_name}({param_placeholders}) as id")
            
            result = db.execute(query, params)
            row = result.fetchone()
            
            if not row or not row.id:
                logger.error(f"Stored procedure {sp_name} returned no ID")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Stored procedure did not return expected ID"
                )
            
            result_id = str(row.id)
            logger.info(f"Successfully executed {sp_name}, returned ID: {result_id}")
            return result_id
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"SQL error in {sp_name}: {e}")
            raise StoredProcedureService._handle_database_error(str(e))
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in {sp_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    def execute_returning_status(db: Session, sp_name: str, params: Dict[str, Any]) -> DocItemStatus:
        """
        Execute stored procedure and return a status enum.
        Used specifically for document review operations.
        
        Args:
            db: Database session
            sp_name: Stored procedure name
            params: Parameters dictionary for the stored procedure
            
        Returns:
            DocItemStatus enum value
            
        Raises:
            HTTPException: With appropriate status code and error message
        """
        logger.debug(f"Executing stored procedure for status: {sp_name} with params: {params}")
        
        try:
            param_placeholders = ", ".join([f":{key}" for key in params.keys()])
            query = text(f"SELECT {sp_name}({param_placeholders}) as status")
            
            result = db.execute(query, params)
            row = result.fetchone()
            
            if not row or not row.status:
                logger.error(f"Stored procedure {sp_name} returned no status")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Review operation failed"
                )
            
            status_value = DocItemStatus(row.status)
            logger.info(f"Successfully executed {sp_name}, returned status: {status_value}")
            return status_value
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except ValueError as e:
            logger.error(f"Invalid status value returned from {sp_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid status returned from database"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"SQL error in {sp_name}: {e}")
            raise StoredProcedureService._handle_database_error(str(e))
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in {sp_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    @staticmethod
    def _handle_database_error(error_message: str) -> HTTPException:
        """
        Convert database error messages to appropriate HTTP exceptions.
        
        Args:
            error_message: Raw database error message
            
        Returns:
            HTTPException with appropriate status code and cleaned message
        """
        # Clean up the error message by removing SQL context information
        clean_message = error_message.split("CONTEXT:")[0].strip()
        clean_message = clean_message.replace("psycopg2.errors.RaiseException:", "").strip()
        
        # Map database errors to HTTP status codes
        lower_message = clean_message.lower()
        
        if "not found" in lower_message:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=clean_message
            )
        elif any(keyword in lower_message for keyword in ["role", "permission", "manufacturer", "safety_manager"]):
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=clean_message
            )
        elif any(keyword in lower_message for keyword in ["conflict", "already", "duplicate", "overlapping"]):
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=clean_message
            )
        elif "invalid" in lower_message or "constraint" in lower_message:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=clean_message
            )
        else:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=clean_message
            )


class ValidationService:
    """Service for application-layer validations."""
    
    @staticmethod
    def validate_file_url(file_url: str) -> None:
        """
        Validate file URL meets security requirements.
        This is application-layer validation before database processing.
        
        Args:
            file_url: URL to validate
            
        Raises:
            HTTPException: If URL doesn't meet requirements
        """
        logger.debug(f"Validating file URL: {file_url}")
        
        # Check HTTPS requirement
        if not file_url.startswith(config.REQUIRED_URL_SCHEME + "://"):
            logger.warning(f"File URL rejected - not HTTPS: {file_url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {config.REQUIRED_URL_SCHEME.upper()} URLs are allowed"
            )
        
        # Check file extension
        if not any(file_url.lower().endswith(ext) for ext in config.ALLOWED_FILE_EXTENSIONS):
            logger.warning(f"File URL rejected - invalid extension: {file_url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed extensions: {', '.join(config.ALLOWED_FILE_EXTENSIONS)}"
            )
        
        logger.info(f"File URL validation passed: {file_url}")
    
    @staticmethod
    def validate_organization_for_cranes(db: Session, owner_org_id: str) -> None:
        """
        Validate that organization exists and is of OWNER type for crane operations.
        
        Args:
            db: Database session
            owner_org_id: Organization ID to validate
            
        Raises:
            HTTPException: If organization doesn't exist or wrong type
        """
        logger.debug(f"Validating organization for cranes: {owner_org_id}")
        
        org = db.get(Org, owner_org_id)
        if not org:
            logger.warning(f"Organization not found: {owner_org_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        if org.type != OrgType.OWNER:
            logger.warning(f"Organization {owner_org_id} is not an owner type: {org.type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is not an owner type"
            )
        
        logger.info(f"Organization validation passed: {org.name} ({org.type})")


class CraneService:
    """Service for crane-related operations."""
    
    @staticmethod
    def list_owner_cranes(db: Session, owner_org_id: str) -> List[Crane]:
        """
        List all cranes owned by a specific organization.
        
        Args:
            db: Database session
            owner_org_id: Organization ID
            
        Returns:
            List of Crane instances
            
        Raises:
            HTTPException: If organization doesn't exist or wrong type
        """
        logger.debug(f"Listing cranes for organization: {owner_org_id}")
        
        # Get cranes using optimized query
        cranes = db.query(Crane).filter(
            Crane.owner_org_id == owner_org_id
        ).order_by(Crane.model_name).all()
        
        # If no cranes found, validate organization exists to provide better error message
        if not cranes:
            ValidationService.validate_organization_for_cranes(db, owner_org_id)
            # If validation passes, organization exists but has no cranes - return empty list
            logger.info(f"No cranes found for organization: {owner_org_id}")
            return []
        
        logger.info(f"Found {len(cranes)} cranes for organization: {owner_org_id}")
        return cranes