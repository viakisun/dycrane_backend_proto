import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# This is a standalone script, so we need to set up the path
# to import from the server directory.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.database import db_manager
from server.domain.models import Org, User, Crane, UserOrg, CraneModel
from server.domain.schemas import OrgType, UserRole, CraneStatus
import json
import random

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
    {"id": "user-safety-manager-01", "email": "safety1@example.com", "name": "Safety Manager One", "role": UserRole.SAFETY_MANAGER},
    {"id": "user-manufacturer-01", "email": "mfr1@example.com", "name": "Manufacturer Admin", "role": UserRole.MANUFACTURER, "org_id": "org-mfg-01"},
    {"id": "user-owner-01", "email": "owner1@example.com", "name": "Owner One (Total)", "role": UserRole.OWNER, "org_id": "org-owner-01"},
    {"id": "user-owner-02", "email": "owner2@example.com", "name": "Owner Two (Apex)", "role": UserRole.OWNER, "org_id": "org-owner-02"},
    {"id": "user-owner-03", "email": "owner3@example.com", "name": "Owner Three (Summit)", "role": UserRole.OWNER, "org_id": "org-owner-03"},
    {"id": "user-owner-04", "email": "owner4@example.com", "name": "Owner Four (Bedrock)", "role": UserRole.OWNER, "org_id": "org-owner-04"},
    {"id": "user-owner-05", "email": "owner5@example.com", "name": "Owner Five (SkyHigh)", "role": UserRole.OWNER, "org_id": "org-owner-05"},
    {"id": "user-driver-01", "email": "driver1@example.com", "name": "Driver A", "role": UserRole.DRIVER},
    {"id": "user-driver-02", "email": "driver2@example.com", "name": "Driver B", "role": UserRole.DRIVER},
    {"id": "user-driver-03", "email": "driver3@example.com", "name": "Driver C", "role": UserRole.DRIVER},
]

CRANE_MODELS = [
    {
        "model_name": "SS1926", "max_lifting_capacity_ton_m": 18, "max_working_height_m": 22.7, "max_working_radius_m": 19.8,
        "iver_torque_phi_mm": "10x100", "boom_sections": 6, "tele_speed_m_sec": "15.1/36", "boom_angle_speed_deg_sec": "80/17",
        "lifting_load_distance_kg_m": json.dumps([{"load": 5600, "distance": 30}, {"load": 3800, "distance": 47}, {"load": 2100, "distance": 77}, {"load": 1700, "distance": 87}, {"load": 850, "distance": 137}, {"load": 500, "distance": 168}, {"load": 390, "distance": 207}]),
        "optional_specs": ["SUB WINCH"]
    },
    {
        "model_name": "SS1406", "max_lifting_capacity_ton_m": 14, "max_working_height_m": 18.3, "max_working_radius_m": 16.35,
        "iver_torque_phi_mm": "10x90", "boom_sections": 5, "tele_speed_m_sec": "12.3/32", "boom_angle_speed_deg_sec": "78/12.5",
        "lifting_load_distance_kg_m": json.dumps([{"load": 5600, "distance": 28}, {"load": 3500, "distance": 40}, {"load": 2000, "distance": 62}, {"load": 1600, "distance": 69}, {"load": 850, "distance": 114}, {"load": 700, "distance": 132}, {"load": 450, "distance": 163}]),
        "optional_specs": ["SUB WINCH"]
    },
    {
        "model_name": "ST2217D", "max_lifting_capacity_ton_m": 22, "max_working_height_m": 25.7, "max_working_radius_m": 22.6,
        "iver_torque_phi_mm": "10x100", "boom_sections": 7, "tele_speed_m_sec": "17.8/25", "boom_angle_speed_deg_sec": "-17~80/19",
        "lifting_load_distance_kg_m": json.dumps([{"load": 6000, "distance": 30}, {"load": 4500, "distance": 48}, {"load": 3200, "distance": 76}, {"load": 1800, "distance": 113}, {"load": 1000, "distance": 138}, {"load": 750, "distance": 167}, {"load": 500, "distance": 207}]),
        "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "SS2037D", "max_lifting_capacity_ton_m": 22, "max_working_height_m": 25.7, "max_working_radius_m": 22.6,
        "iver_torque_phi_mm": "10x100", "boom_sections": 7, "tele_speed_m_sec": "17.8/37", "boom_angle_speed_deg_sec": "-17~80/19",
        "lifting_load_distance_kg_m": None, "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "ST2217", "max_lifting_capacity_ton_m": 22, "max_working_height_m": 22.7, "max_working_radius_m": 19.8,
        "iver_torque_phi_mm": "10x100", "boom_sections": 6, "tele_speed_m_sec": "17.1/23", "boom_angle_speed_deg_sec": "-17~80/19",
        "lifting_load_distance_kg_m": None, "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "SS2036Ace", "max_lifting_capacity_ton_m": 22, "max_working_height_m": 22.7, "max_working_radius_m": 19.8,
        "iver_torque_phi_mm": "10x100", "boom_sections": 6, "tele_speed_m_sec": "15.1/36", "boom_angle_speed_deg_sec": "-17~80/19",
        "lifting_load_distance_kg_m": json.dumps([{"load": 8000, "distance": 30}, {"load": 4500, "distance": 47}, {"load": 3200, "distance": 77}, {"load": 1800, "distance": 113}, {"load": 1000, "distance": 137}, {"load": 800, "distance": 168}, {"load": 600, "distance": 188}]),
        "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "ST2516", "max_lifting_capacity_ton_m": 24, "max_working_height_m": 29.5, "max_working_radius_m": 26,
        "iver_torque_phi_mm": "12x120", "boom_sections": 6, "tele_speed_m_sec": "19.8/26", "boom_angle_speed_deg_sec": "-15~80/23",
        "lifting_load_distance_kg_m": json.dumps([{"load": 12000, "distance": 30}, {"load": 5700, "distance": 61}, {"load": 2400, "distance": 101}, {"load": 1400, "distance": 141}, {"load": 950, "distance": 181}, {"load": 700, "distance": 220}, {"load": 500, "distance": 260}]),
        "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "ST2517", "max_lifting_capacity_ton_m": 25, "max_working_height_m": 26.5, "max_working_radius_m": 23.5,
        "iver_torque_phi_mm": "12x120", "boom_sections": 7, "tele_speed_m_sec": "18.5/27", "boom_angle_speed_deg_sec": "-15~80/23",
        "lifting_load_distance_kg_m": json.dumps([{"load": 12000, "distance": 30}, {"load": 6400, "distance": 50}, {"load": 3300, "distance": 81}, {"load": 1900, "distance": 112}, {"load": 1300, "distance": 143}, {"load": 1000, "distance": 174}, {"load": 700, "distance": 204}, {"load": 500, "distance": 233}]),
        "optional_specs": ["SUB WINCH", "SUB BOOM", "DY-CABIN"]
    },
    {
        "model_name": "ST7516", "max_lifting_capacity_ton_m": 70, "max_working_height_m": 34.5, "max_working_radius_m": 30.6,
        "iver_torque_phi_mm": "14x150", "boom_sections": 6, "tele_speed_m_sec": "23.2/40", "boom_angle_speed_deg_sec": "-10~80/30",
        "lifting_load_distance_kg_m": json.dumps([{"load": 20000, "distance": 30}, {"load": 8398, "distance": 74}, {"load": 4750, "distance": 120}, {"load": 2792, "distance": 164}, {"load": 2000, "distance": 213}, {"load": 1480, "distance": 269}, {"load": 1000, "distance": 352}]),
        "optional_specs": ["SUB WINCH", "SUB BOOM", "SUBMODULE O/R"]
    },
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

    logger.info("--- Seeding Crane Models ---")
    model_ids = []
    for model_data in CRANE_MODELS:
        model = db.query(CraneModel).filter(CraneModel.model_name == model_data["model_name"]).first()
        if not model:
            model = CraneModel(**model_data)
            db.add(model)
    db.commit()
    # Get all model IDs to randomly assign them later
    model_ids = [m.id for m in db.query(CraneModel.id).all()]


    logger.info("--- Seeding Crane Instances ---")
    # First, truncate the existing cranes to reset them
    db.execute(text("TRUNCATE TABLE ops.cranes RESTART IDENTITY CASCADE"))

    for i in range(1, 6):
        owner_id = f"org-owner-0{i}"
        for j in range(1, 11):
            status = CraneStatus.NORMAL
            if j % 10 == 0: status = CraneStatus.REPAIR
            elif j % 10 == 9: status = CraneStatus.INBOUND

            serial_no = f"SN-DY-{str(i).zfill(2)}{str(j).zfill(3)}"

            db.add(Crane(
                owner_org_id=owner_id,
                model_id=random.choice(model_ids),
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
