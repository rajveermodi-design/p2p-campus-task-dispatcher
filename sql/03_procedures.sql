-- ============================================================================
-- SCRIPT: 03_procedures.sql
-- PROJECT: Peer-to-Peer Campus Task & Errand Dispatcher
-- DESCRIPTION: Houses transactional stored procedures with row-level locks
--              (FOR UPDATE), ACID boundary isolation, and balance transfers.
-- ============================================================================

DELIMITER //

-- ----------------------------------------------------------------------------
-- PROCEDURE 1: sp_post_task_with_escrow
-- Atomically checks requester balance, locks the row, deducts funds, creates
-- the task record, and locks funds into escrow in a single ACID transaction.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_post_task_with_escrow //
CREATE PROCEDURE sp_post_task_with_escrow(
    IN p_requester_id VARCHAR(12),
    IN p_pickup VARCHAR(100),
    IN p_drop VARCHAR(100),
    IN p_bounty DECIMAL(8,2),
    IN p_pin CHAR(4)
)
BEGIN
    DECLARE v_balance DECIMAL(10,2);
    DECLARE v_new_task_id INT;

    -- Rollback on any internal failure
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Row-level exclusive lock on requester to prevent double-spending
    SELECT Balance INTO v_balance
    FROM Students
    WHERE Reg_No = p_requester_id
    FOR UPDATE;

    -- Validate sufficient funds
    IF v_balance < p_bounty THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Transaction Rejected: Insufficient balance for escrow bounty';
    END IF;

    -- Step 1: Deduct bounty from requester wallet
    UPDATE Students
    SET Balance = Balance - p_bounty
    WHERE Reg_No = p_requester_id;

    -- Step 2: Post the task into open state
    INSERT INTO Tasks (
        Requester_ID, 
        Pickup_Location, 
        Drop_Location, 
        Bounty, 
        Status, 
        Verification_Pin
    )
    VALUES (
        p_requester_id, 
        p_pickup, 
        p_drop, 
        p_bounty, 
        'open', 
        p_pin
    );

    SET v_new_task_id = LAST_INSERT_ID();

    -- Step 3: Isolate bounty funds in the Escrow ledger
    INSERT INTO Escrow_Transactions (Task_ID, Amount, Escrow_State)
    VALUES (v_new_task_id, p_bounty, 'HELD');

    COMMIT;
END //

-- ----------------------------------------------------------------------------
-- PROCEDURE 2: sp_assign_runner_to_task
-- Solves the "Simultaneous Claim" race condition. Places an exclusive row lock
-- on the task; the first runner transitions it, subsequent runners fail cleanly.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_assign_runner_to_task //
CREATE PROCEDURE sp_assign_runner_to_task(
    IN p_task_id INT,
    IN p_runner_id VARCHAR(12)
)
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_requester_id VARCHAR(12);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Acquire exclusive row lock (X-lock) on the task
    SELECT Status, Requester_ID INTO v_status, v_requester_id
    FROM Tasks
    WHERE Task_ID = p_task_id
    FOR UPDATE;

    -- Verify the task is still open
    IF v_status <> 'open' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Conflict: Task has already been claimed or is unavailable';
    END IF;

    -- Prevent requester from claiming their own task
    IF v_requester_id = p_runner_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Constraint Violation: Requester cannot act as runner for own task';
    END IF;

    -- Update task to assigned (fires trg_after_task_assignment trigger)
    UPDATE Tasks
    SET Runner_ID = p_runner_id,
        Status = 'assigned'
    WHERE Task_ID = p_task_id;

    COMMIT;
END //

-- ----------------------------------------------------------------------------
-- PROCEDURE 3: sp_complete_task_handover (WITH BUG FIX)
-- Validates runner identity and 4-digit PIN before releasing escrow funds.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_complete_task_handover //
CREATE PROCEDURE sp_complete_task_handover(
    IN p_task_id INT,
    IN p_runner_id VARCHAR(12),
    IN p_input_pin CHAR(4)
)
BEGIN
    DECLARE v_correct_pin CHAR(4);
    DECLARE v_status VARCHAR(20);
    DECLARE v_bounty DECIMAL(8,2);
    DECLARE v_assigned_runner VARCHAR(12);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Exclusive lock on the specific task row
    SELECT Verification_Pin, Status, Bounty, Runner_ID
    INTO v_correct_pin, v_status, v_bounty, v_assigned_runner
    FROM Tasks
    WHERE Task_ID = p_task_id
    FOR UPDATE;

    -- 1. Validate lifecycle state
    IF v_status NOT IN ('assigned', 'in_transit') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid State: Task is not active or awaiting completion';
    END IF;

    -- 2. Validate runner identity (BUG FIX: verify caller against assigned runner)
    IF v_assigned_runner IS NULL OR v_assigned_runner <> p_runner_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Unauthorized: Caller is not the runner assigned to this task';
    END IF;

    -- 3. Cryptographic token match
    IF v_correct_pin <> p_input_pin THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Authentication Failed: Invalid verification PIN';
    END IF;

    -- Step A: Mark task complete
    UPDATE Tasks 
    SET Status = 'completed' 
    WHERE Task_ID = p_task_id;

    -- Step B: Transition escrow ledger to RELEASED
    UPDATE Escrow_Transactions
    SET Escrow_State = 'RELEASED', 
        Released_At = CURRENT_TIMESTAMP
    WHERE Task_ID = p_task_id;

    -- Step C: Credit runner account balance
    UPDATE Students
    SET Balance = Balance + v_bounty
    WHERE Reg_No = p_runner_id;

    COMMIT;
END //

-- ----------------------------------------------------------------------------
-- PROCEDURE 4: sp_refund_abandoned_task
-- Recovers locked funds when a runner abandons a task or a task expires.
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_refund_abandoned_task //
CREATE PROCEDURE sp_refund_abandoned_task(
    IN p_task_id INT
)
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_requester_id VARCHAR(12);
    DECLARE v_escrow_amount DECIMAL(8,2);
    DECLARE v_escrow_state VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Lock both Task and Escrow records
    SELECT Status, Requester_ID INTO v_status, v_requester_id
    FROM Tasks
    WHERE Task_ID = p_task_id
    FOR UPDATE;

    SELECT Amount, Escrow_State INTO v_escrow_amount, v_escrow_state
    FROM Escrow_Transactions
    WHERE Task_ID = p_task_id
    FOR UPDATE;

    -- Validate that escrow funds are currently locked
    IF v_escrow_state <> 'HELD' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Refund Error: Escrow funds are not in HELD state';
    END IF;

    -- Transition task state to cancelled
    UPDATE Tasks
    SET Status = 'cancelled'
    WHERE Task_ID = p_task_id;

    -- Update escrow ledger to REFUNDED
    UPDATE Escrow_Transactions
    SET Escrow_State = 'REFUNDED',
        Released_At = CURRENT_TIMESTAMP
    WHERE Task_ID = p_task_id;

    -- Return funds to requester's student balance
    UPDATE Students
    SET Balance = Balance + v_escrow_amount
    WHERE Reg_No = v_requester_id;

    COMMIT;
END //

DELIMITER ;