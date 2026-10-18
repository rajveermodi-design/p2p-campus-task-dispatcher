-- ============================================================================
-- SCRIPT: 01_schema_ddl.sql
-- PROJECT: Peer-to-Peer Campus Task & Errand Dispatcher
-- DESCRIPTION: Initializes core relational schema normalized to BCNF with
--              strict domain constraints and InnoDB transactional support.
-- ============================================================================

-- Disable foreign key checks during teardown to avoid drop order conflicts
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Escrow_Transactions;
DROP TABLE IF EXISTS Bids;
DROP TABLE IF EXISTS Tasks;
DROP TABLE IF EXISTS Students;

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------------------------------------------------------
-- 1. STUDENTS TABLE
-- Master ledger of verified campus participants, reputations, and wallet funds.
-- ----------------------------------------------------------------------------
CREATE TABLE Students (
    Reg_No VARCHAR(12) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Trust_Rating DECIMAL(3, 2) NOT NULL DEFAULT 5.00,
    Balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Primary & Candidate Keys
    CONSTRAINT pk_students PRIMARY KEY (Reg_No),
    CONSTRAINT uq_students_email UNIQUE (Email),

    -- Domain Integrity Constraints
    CONSTRAINT chk_balance_non_negative CHECK (Balance >= 0.00),
    CONSTRAINT chk_rating_range CHECK (Trust_Rating >= 1.00 AND Trust_Rating <= 5.00),

    -- Institutional Identity Guards (Regex)
    CONSTRAINT chk_reg_no_format 
        CHECK (REGEXP_LIKE(Reg_No, '^[0-9]{2}[A-Z]{3}[0-9]{4}$')),
    CONSTRAINT chk_email_domain 
        CHECK (REGEXP_LIKE(Email, '^[A-Za-z0-9._%+-]+@vitstudent\\.ac\\.in$'))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------------------------------------------------------
-- 2. TASKS TABLE
-- Stores micro-errands, routing endpoints, assignment states, and verification tokens.
-- ----------------------------------------------------------------------------
CREATE TABLE Tasks (
    Task_ID INT AUTO_INCREMENT NOT NULL,
    Requester_ID VARCHAR(12) NOT NULL,
    Runner_ID VARCHAR(12) DEFAULT NULL,
    Pickup_Location VARCHAR(100) NOT NULL,
    Drop_Location VARCHAR(100) NOT NULL,
    Bounty DECIMAL(8, 2) NOT NULL,
    Status ENUM('open', 'assigned', 'in_transit', 'completed', 'cancelled') NOT NULL DEFAULT 'open',
    Verification_Pin CHAR(4) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Primary Key
    CONSTRAINT pk_tasks PRIMARY KEY (Task_ID),

    -- Foreign Key Integrity (RESTRICT prevents error 3823 with CHECK constraint)
    CONSTRAINT fk_tasks_requester FOREIGN KEY (Requester_ID) 
        REFERENCES Students(Reg_No) ON DELETE RESTRICT,
    CONSTRAINT fk_tasks_runner FOREIGN KEY (Runner_ID) 
        REFERENCES Students(Reg_No) ON DELETE RESTRICT,

    -- Domain Integrity Constraints
    CONSTRAINT chk_requester_runner_distinct CHECK (Requester_ID <> Runner_ID),
    CONSTRAINT chk_bounty_positive CHECK (Bounty > 0.00)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------------------------------------------------------
-- 3. BIDS TABLE
-- Tracks competitive runner bids for available tasks.
-- ----------------------------------------------------------------------------
CREATE TABLE Bids (
    Bid_ID INT AUTO_INCREMENT NOT NULL,
    Task_ID INT NOT NULL,
    Runner_ID VARCHAR(12) NOT NULL,
    Offered_Time TIMESTAMP NOT NULL,
    Bid_Status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Primary & Candidate Keys
    CONSTRAINT pk_bids PRIMARY KEY (Bid_ID),
    CONSTRAINT uq_task_runner UNIQUE (Task_ID, Runner_ID),

    -- Foreign Key Integrity
    CONSTRAINT fk_bids_task FOREIGN KEY (Task_ID) 
        REFERENCES Tasks(Task_ID) ON DELETE CASCADE,
    CONSTRAINT fk_bids_runner FOREIGN KEY (Runner_ID) 
        REFERENCES Students(Reg_No) ON DELETE RESTRICT
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ----------------------------------------------------------------------------
-- 4. ESCROW_TRANSACTIONS TABLE
-- Financial isolation ledger decoupling active bounties from general student balances.
-- ----------------------------------------------------------------------------
CREATE TABLE Escrow_Transactions (
    Txn_ID INT AUTO_INCREMENT NOT NULL,
    Task_ID INT NOT NULL,
    Amount DECIMAL(8, 2) NOT NULL,
    Escrow_State ENUM('HELD', 'RELEASED', 'REFUNDED') NOT NULL DEFAULT 'HELD',
    Released_At TIMESTAMP NULL DEFAULT NULL,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Primary & Candidate Keys
    CONSTRAINT pk_escrow PRIMARY KEY (Txn_ID),
    CONSTRAINT uq_escrow_task UNIQUE (Task_ID),

    -- Foreign Key Integrity
    CONSTRAINT fk_escrow_task FOREIGN KEY (Task_ID) 
        REFERENCES Tasks(Task_ID) ON DELETE RESTRICT,

    -- Domain Integrity Constraints
    CONSTRAINT chk_escrow_amount_positive CHECK (Amount > 0.00)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;