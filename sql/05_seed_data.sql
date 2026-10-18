-- ============================================================================
-- SCRIPT: 05_seed_data.sql
-- PROJECT: Peer-to-Peer Campus Task & Errand Dispatcher
-- DESCRIPTION: Populates baseline student profiles, active errands, bids,
--              and isolated escrow ledgers for testing and verification.
-- ============================================================================

-- Ensure referential integrity during bulk data loading
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE Escrow_Transactions;
TRUNCATE TABLE Bids;
TRUNCATE TABLE Tasks;
TRUNCATE TABLE Students;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. SEED STUDENTS
-- Sample students representing requesters, runners, and edge-case profiles.
-- ----------------------------------------------------------------------------
INSERT INTO Students (Reg_No, Name, Email, Trust_Rating, Balance) VALUES
('25BCE0750', 'Rajveer Modi',       'rajveer.modi2025@vitstudent.ac.in',    4.95, 1250.00),
('25BCE0724', 'Yajas AB',           'yajas.ab2025@vitstudent.ac.in',        4.80,  850.00),
('25BCE0717', 'Abhayadev RVM',      'abhayadev.rvm2025@vitstudent.ac.in',   4.90,  620.00),
('25BCE1001', 'Ananya Sharma',      'ananya.sharma2025@vitstudent.ac.in',   4.65,  300.00),
('25BCE1002', 'Karthik Raman',      'karthik.raman2025@vitstudent.ac.in',   4.20,  150.00),
('25BCE1003', 'Rohan Verma',        'rohan.verma2025@vitstudent.ac.in',     3.80,    0.00); -- Edge case: Zero balance account

-- ----------------------------------------------------------------------------
-- 2. SEED TASKS & ESCROW TRANSACTIONS
-- Populating active errands across campus with matched escrow isolation.
-- ----------------------------------------------------------------------------

-- Task 1: Open Errand (Cafeteria food pickup)
-- Requester: Rajveer Modi (25BCE0750)
INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
VALUES (1, '25BCE0750', NULL, 'Food Mall Ground Floor', 'Technology Tower (TT) 412', 60.00, 'open', '4821');

INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
VALUES (1, 1, 60.00, 'HELD', NULL);

-- Task 2: Assigned Errand (Lab record printout handover)
-- Requester: Yajas AB (25BCE0724), Assigned Runner: Abhayadev RVM (25BCE0717)
INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
VALUES (2, '25BCE0724', '25BCE0717', 'Main Library Reprography', 'SJT Block 3rd Floor Lab', 40.00, 'assigned', '9103');

INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
VALUES (2, 2, 40.00, 'HELD', NULL);

-- Task 3: Completed Errand (Hardware component transfer)
-- Requester: Ananya Sharma (25BCE1001), Completed Runner: Karthik Raman (25BCE1002)
INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
VALUES (3, '25BCE1001', '25BCE1002', 'Men''s Hostel Block D', 'Men''s Hostel Block L 204', 50.00, 'completed', '3378');

INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
VALUES (3, 3, 50.00, 'RELEASED', CURRENT_TIMESTAMP);

-- ----------------------------------------------------------------------------
-- 3. SEED BIDS
-- Demonstrates pending, accepted, and rejected bids across errands.
-- ----------------------------------------------------------------------------

-- Bids for Task 1 (Open errand with two competing runners)
INSERT INTO Bids (Bid_ID, Task_ID, Runner_ID, Offered_Time, Bid_Status) VALUES
(1, 1, '25BCE0724', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 20 MINUTE), 'pending'),
(2, 1, '25BCE0717', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 10 MINUTE), 'pending');

-- Bids for Task 2 (Assigned errand reflecting resolution trigger)
INSERT INTO Bids (Bid_ID, Task_ID, Runner_ID, Offered_Time, Bid_Status) VALUES
(3, 2, '25BCE0717', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 45 MINUTE), 'accepted'),
(4, 2, '25BCE1002', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 35 MINUTE), 'rejected');

-- Bids for Task 3 (Completed errand)
INSERT INTO Bids (Bid_ID, Task_ID, Runner_ID, Offered_Time, Bid_Status) VALUES
(5, 3, '25BCE1002', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 90 MINUTE), 'accepted');