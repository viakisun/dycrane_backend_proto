-- Seed baseline data for tests (orgs, users, cranes)
-- Assumes: ops schema exists; uuid-ossp extension available


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SET search_path TO ops, public;


-- Orgs
INSERT INTO orgs (id, name, type) VALUES
(uuid_generate_v4(), 'OwnerOrg-A', 'OWNER'),
(uuid_generate_v4(), 'OwnerOrg-B', 'OWNER'),
(uuid_generate_v4(), 'Manufacturer-VIA', 'MANUFACTURER')
ON CONFLICT DO NOTHING;


-- Users
-- The password for all users is 'password'
-- Hashed with SHA256: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
INSERT INTO users (id, email, name, role, is_active, hashed_password)
VALUES
('user-safety-manager-01', 'safety1@via.local', 'Safety One', 'SAFETY_MANAGER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-safety-manager-02', 'safety2@via.local', 'Safety Two', 'SAFETY_MANAGER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-manufacturer-01', 'mfr@via.local', 'Mfr Admin', 'MANUFACTURER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-01', 'owner@via.local', 'Owner Boss', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-01', 'driver1@via.local', 'Driver A', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-02', 'driver2@via.local', 'Driver B', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-03', 'driver3@via.local', 'Driver C', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
ON CONFLICT (email) DO NOTHING;


-- Map manufacturer and owner user to their orgs
DO $$
DECLARE
v_mfr_org uuid;
v_ownerA uuid;
v_mfr_user uuid;
v_owner_user uuid;
BEGIN
SELECT id INTO v_mfr_org FROM orgs WHERE name='Manufacturer-VIA' LIMIT 1;
SELECT id INTO v_ownerA FROM orgs WHERE name='OwnerOrg-A' LIMIT 1;
SELECT id INTO v_mfr_user FROM users WHERE email='mfr@via.local' LIMIT 1;
SELECT id INTO v_owner_user FROM users WHERE email='owner@via.local' LIMIT 1;


IF v_mfr_org IS NOT NULL AND v_mfr_user IS NOT NULL THEN
INSERT INTO user_orgs(user_id, org_id) VALUES (v_mfr_user, v_mfr_org)
ON CONFLICT DO NOTHING;
END IF;


IF v_ownerA IS NOT NULL AND v_owner_user IS NOT NULL THEN
INSERT INTO user_orgs(user_id, org_id) VALUES (v_owner_user, v_ownerA)
ON CONFLICT DO NOTHING;
END IF;
END$$;


-- Cranes for OwnerOrg-A and OwnerOrg-B
DO $$
DECLARE
v_ownerA uuid;
v_ownerB uuid;
BEGIN
SELECT id INTO v_ownerA FROM orgs WHERE name='OwnerOrg-A' LIMIT 1;
SELECT id INTO v_ownerB FROM orgs WHERE name='OwnerOrg-B' LIMIT 1;


IF v_ownerA IS NOT NULL THEN
INSERT INTO cranes(id, owner_org_id, model_name, serial_no, status) VALUES
(uuid_generate_v4(), v_ownerA, 'TRUCK-60T', 'SN-TRK-001', 'NORMAL'),
(uuid_generate_v4(), v_ownerA, 'TRUCK-60T', 'SN-TRK-002', 'REPAIR'),
(uuid_generate_v4(), v_ownerA, 'CRAWLER-120T', 'SN-CRW-010', 'NORMAL')
ON CONFLICT (serial_no) DO NOTHING;
END IF;


IF v_ownerB IS NOT NULL THEN
INSERT INTO cranes(id, owner_org_id, model_name, serial_no, status) VALUES
(uuid_generate_v4(), v_ownerB, 'TRUCK-80T', 'SN-TRK-080', 'INBOUND'),
(uuid_generate_v4(), v_ownerB, 'CRAWLER-200T', 'SN-CRW-200', 'NORMAL')
ON CONFLICT (serial_no) DO NOTHING;
END IF;
END$$;