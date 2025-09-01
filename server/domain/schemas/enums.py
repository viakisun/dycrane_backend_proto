from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    DRIVER = "DRIVER"
    SAFETY_MANAGER = "SAFETY_MANAGER"
    OWNER = "OWNER"
    MANUFACTURER = "MANUFACTURER"


class SiteStatus(str, Enum):
    """Construction site status values."""

    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class CraneStatus(str, Enum):
    """Crane operational status values."""

    NORMAL = "NORMAL"  # Available for assignment
    REPAIR = "REPAIR"  # Under maintenance
    INBOUND = "INBOUND"  # Being transported


class AssignmentStatus(str, Enum):
    """Assignment status for both crane and driver assignments."""

    ASSIGNED = "ASSIGNED"
    RELEASED = "RELEASED"


class DocItemStatus(str, Enum):
    """Document item review status."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RequestType(str, Enum):
    """Generic request types."""

    CRANE_DEPLOY = "CRANE_DEPLOY"


class RequestStatus(str, Enum):
    """Generic request statuses."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class OrgType(str, Enum):
    """Organization type classification."""

    OWNER = "OWNER"  # Construction company owning cranes
    MANUFACTURER = "MANUFACTURER"  # Crane manufacturer providing approval
