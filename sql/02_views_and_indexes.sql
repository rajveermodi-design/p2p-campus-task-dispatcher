-- ============================================================================
-- SCRIPT: 02_views_and_indexes.sql
-- PROJECT: Peer-to-Peer Campus Task & Errand Dispatcher
-- DESCRIPTION: Creates secure public-facing views and composite B-Tree indexes
--              to optimize high-concurrency feeds and analytical queries.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VIEWS
-- ----------------------------------------------------------------------------

-- Drop view if it already exists
DROP VIEW IF EXISTS Active_Open_Tasks_View;

-- Abstracted Live Marketplace Feed View
-- Shields sensitive tokens (Verification_Pin, requester balances) from client consumers
CREATE VIEW Active_Open_Tasks_View AS
SELECT 
    t.Task_ID,
    t.Pickup_Location,
    t.Drop_Location,
    t.Bounty,
    s.Name AS Requester_Name,
    s.Trust_Rating AS Requester_Rating,
    t.Created_At
FROM Tasks t
JOIN Students s ON t.Requester_ID = s.Reg_No
WHERE t.Status = 'open';

-- ----------------------------------------------------------------------------
-- 2. INDEXING SCHEME
-- ----------------------------------------------------------------------------

-- Index 1: Composite index on Task Status and Primary Key
-- Eliminates table scans on marketplace feeds by narrowing directly to 'open' tasks
CREATE INDEX idx_tasks_status_id ON Tasks(Status, Task_ID);

-- Index 2: Runner-centric bid status index
-- Optimizes queries checking active bids submitted by a specific runner
CREATE INDEX idx_bids_runner_status ON Bids(Runner_ID, Bid_Status);