import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# This is a standalone script, so we need to set up the path
# to import from the server directory.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import db_manager
from server.domain.models import Org, User, Crane, UserOrg
from server.domain.schemas import OrgType, UserRole, CraneStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hashed password for 'password'
HASHED_PASSWORD = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

ORGS = [
    {"id": "org-owner-01", "name": "Total Cranes Inc.", "type": OrgType.OWNER},
    {"id": "org-owner-02", "name": "Apex Lifting Solutions", "type": OrgType.OWNER},
    {"id": "org-owner-03", "name": "Summit Hoisting", "type": OrgType.OWNER},
    {"id": "org-owner-04", "name": "Bedrock Heavy Machinery", "type": OrgType.OWNER},
    {"id": "org-owner-05", "name": "SkyHigh Rentals", "type": OrgType.OWNER},
    {"id": "org-mfg-01", "name": "Global Crane Manufacturing", "type": OrgType.MANUFACTURER},
]

USERS = [
    {"id": "user-safety-manager-01", "email": "safety1@dy.local", "name": "Safety Manager One", "role": UserRole.SAFETY_MANAGER},
    {"id": "user-manufacturer-01", "email": "mfr1@dy.local", "name": "Manufacturer Admin", "role": UserRole.MANUFACTURER, "org_id": "org-mfg-01"},
    {"id": "user-owner-01", "email": "owner1@dy.local", "name": "Owner One (Total)", "role": UserRole.OWNER, "org_id": "org-owner-01"},
    {"id": "user-owner-02", "email": "owner2@dy.local", "name": "Owner Two (Apex)", "role": UserRole.OWNER, "org_id": "org-owner-02"},
    {"id": "user-owner-03", "email": "owner3@dy.local", "name": "Owner Three (Summit)", "role": UserRole.OWNER, "org_id": "org-owner-03"},
    {"id": "user-owner-04", "email": "owner4@dy.local", "name": "Owner Four (Bedrock)", "role": UserRole.OWNER, "org_id": "org-owner-04"},
    {"id": "user-owner-05", "email": "owner5@dy.local", "name": "Owner Five (SkyHigh)", "role": UserRole.OWNER, "org_id": "org-owner-05"},
    {"id": "user-driver-01", "email": "driver1@dy.local", "name": "Driver A", "role": UserRole.DRIVER},
    {"id": "user-driver-02", "email": "driver2@dy.local", "name": "Driver B", "role": UserRole.DRIVER},
    {"id": "user-driver-03", "email": "driver3@dy.local", "name": "Driver C", "role": UserRole.DRIVER},
]

def seed_data(db: Session):
    logger.info("--- Seeding Organizations ---")
    for org_data in ORGS:
        org = db.query(Org).filter(Org.id == org_data["id"]).first()
        if not org:
            db.add(Org(**org_data))
    db.commit()

    logger.info("--- Seeding Users and User-Org Mappings ---")
    for user_data in USERS:
        org_id = user_data.pop("org_id", None)
        user = db.query(User).filter(User.id == user_data["id"]).first()
        if not user:
            user = User(**user_data, hashed_password=HASHED_PASSWORD)
            db.add(user)
        if org_id:
            user_org = db.query(UserOrg).filter(UserOrg.user_id == user.id, UserOrg.org_id == org_id).first()
            if not user_org:
                db.add(UserOrg(user_id=user.id, org_id=org_id))
    db.commit()

    logger.info("--- Seeding Cranes ---")
    for i in range(1, 6):
        owner_id = f"org-owner-0{i}"
        for j in range(1, 11):
            if j <= 5:
                model, prefix = "TRUCK-80T", "TRK80"
            else:
                model, prefix = "CRAWLER-150T", "CRW150"

            status = CraneStatus.NORMAL
            if j % 10 == 0: status = CraneStatus.REPAIR
            elif j % 10 == 9: status = CraneStatus.INBOUND

            serial_no = f"SN-{prefix}-{str(i).zfill(2)}{str(j).zfill(3)}"
            crane = db.query(Crane).filter(Crane.serial_no == serial_no).first()
            if not crane:
                db.add(Crane(
                    owner_org_id=owner_id,
                    model_name=model,
                    serial_no=serial_no,
                    status=status
                ))
    db.commit()
    logger.info("--- Seeding complete ---")

if __name__ == "__main__":
    logger.info("Starting procedural seeding...")
    with db_manager.get_session() as db:
        try:
            seed_data(db)
        except IntegrityError as e:
            logger.error(f"Integrity error during seeding, data likely already exists: {e}")
            db.rollback()
        except Exception as e:
            logger.error(f"An error occurred during seeding: {e}")
            db.rollback()
            raise
    logger.info("Seeding process finished.")
