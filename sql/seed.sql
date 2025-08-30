-- Seed baseline data for tests (orgs, users, cranes)
-- Assumes: ops schema exists; uuid-ossp extension available


CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
SET search_path TO ops, public;


-- Orgs
INSERT INTO orgs (id, name, type) VALUES
('org-owner-01', 'Total Cranes Inc.', 'OWNER'),
('org-owner-02', 'Apex Lifting Solutions', 'OWNER'),
('org-owner-03', 'Summit Hoisting', 'OWNER'),
('org-owner-04', 'Bedrock Heavy Machinery', 'OWNER'),
('org-owner-05', 'SkyHigh Rentals', 'OWNER'),
('org-mfg-01', 'Global Crane Manufacturing', 'MANUFACTURER')
ON CONFLICT (id) DO NOTHING;


-- Users
-- The password for all users is 'password'
-- Hashed with SHA256: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
INSERT INTO users (id, email, name, role, is_active, hashed_password)
VALUES
('user-safety-manager-01', 'safety1@dy.local', 'Safety Manager One', 'SAFETY_MANAGER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-safety-manager-02', 'safety2@dy.local', 'Safety Manager Two', 'SAFETY_MANAGER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-manufacturer-01', 'mfr1@dy.local', 'Manufacturer Admin', 'MANUFACTURER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-01', 'owner1@dy.local', 'Owner One (Total)', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-02', 'owner2@dy.local', 'Owner Two (Apex)', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-03', 'owner3@dy.local', 'Owner Three (Summit)', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-04', 'owner4@dy.local', 'Owner Four (Bedrock)', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-owner-05', 'owner5@dy.local', 'Owner Five (SkyHigh)', 'OWNER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-01', 'driver1@dy.local', 'Driver A', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-02', 'driver2@dy.local', 'Driver B', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-03', 'driver3@dy.local', 'Driver C', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-04', 'driver4@dy.local', 'Driver D', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
('user-driver-05', 'driver5@dy.local', 'Driver E', 'DRIVER', TRUE, '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email, name = EXCLUDED.name;


-- Map manufacturer and owner user to their orgs
DO $$
DECLARE
v_mfr_org TEXT;
v_ownerA TEXT;
v_mfr_user TEXT;
v_owner_user TEXT;
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
v_ownerA TEXT;
v_ownerB TEXT;
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