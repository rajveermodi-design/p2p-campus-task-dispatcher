-- ============================================================================
-- SCRIPT: 04_triggers.sql
-- PROJECT: Peer-to-Peer Campus Task & Errand Dispatcher
-- DESCRIPTION: Event-driven triggers enforcing active marketplace integrity
--              and automated bid state resolutions.
-- ============================================================================

DELIMITER //

-- ----------------------------------------------------------------------------
-- TRIGGER 1: trg_prevent_self_bid
-- FIRES: BEFORE INSERT ON Bids
-- PURPOSE: Stops a student from bidding on tasks they posted themselves,
--          preventing trust rating inflation and marketplace manipulation.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_self_bid //
CREATE TRIGGER trg_prevent_self_bid
BEFORE INSERT ON Bids
FOR EACH ROW
BEGIN
    DECLARE v_requester_id VARCHAR(12);

    -- Query parent task to identify the original poster
    SELECT Requester_ID INTO v_requester_id
    FROM Tasks
    WHERE Task_ID = NEW.Task_ID;

    -- Block the transaction if the runner is the requester
    IF v_requester_id = NEW.Runner_ID THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Constraint violation: Requester cannot bid on their own task';
    END IF;
END //

-- ----------------------------------------------------------------------------
-- TRIGGER 2: trg_after_task_assignment
-- FIRES: AFTER UPDATE ON Tasks
-- PURPOSE: When a runner is assigned to a task, automatically accepts the
--          winning bid and rejects all other competing runner bids.
-- ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_task_assignment //
CREATE TRIGGER trg_after_task_assignment
AFTER UPDATE ON Tasks
FOR EACH ROW
BEGIN
    -- Check if the task transitioned from unassigned to assigned
    IF OLD.Runner_ID IS NULL AND NEW.Runner_ID IS NOT NULL THEN
        -- Mark the winning runner's bid as accepted
        UPDATE Bids
        SET Bid_Status = 'accepted'
        WHERE Task_ID = NEW.Task_ID AND Runner_ID = NEW.Runner_ID;

        -- Mark all remaining competing bids as rejected
        UPDATE Bids
        SET Bid_Status = 'rejected'
        WHERE Task_ID = NEW.Task_ID AND Runner_ID <> NEW.Runner_ID;
    END IF;
END //

DELIMITER ;