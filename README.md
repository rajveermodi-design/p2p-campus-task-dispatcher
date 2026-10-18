# Peer-to-Peer Campus Task & Errand Dispatcher


## 1. Executive Summary & Core Concept

The **Peer-to-Peer Campus Task & Errand Dispatcher** is a high-concurrency relational database platform engineered to manage student micro-errands (such as cafeteria food runs, document printouts, and peer item transfers) across a university campus.

### The Air Traffic Control Analogy
* **Pilots (Peer Runners):** Students browsing and bidding on available errands across campus.
* **Flight Paths (Active Tasks):** Errand postings containing pickup/drop coordinates, financial bounties, and 4-digit verification PINs.
* **Air Traffic Controller (Relational DBMS):** The InnoDB transactional engine that locks assigned flight paths, prevents mid-air collisions (simultaneous task claims or double-spending), and guarantees consistent state transitions via ACID transactions.

**Core Architectural Philosophy:** Rather than relying on vulnerable application-level checks, all mission-critical state transitions, financial escrow holds, and concurrency guards are enforced directly inside the relational database tier using **Stored Procedures, Triggers, Check Constraints, and Pessimistic Row-Level Locking (`SELECT ... FOR UPDATE`)**.

---

## 2. System Architecture & Module Breakdown

The system is structured into four tightly integrated relational modules:

1. **Module 1: BCNF Relational Schema & Identity Ledger (`Students`, `Tasks`)**
   * Enforces strict domain integrity using `CHECK` constraints (`Balance >= 0.00`, `Trust_Rating BETWEEN 1.00 AND 5.00`, `Bounty > 0.00`, and `Requester_ID <> Runner_ID`).
   * Eliminates data redundancy and update anomalies through full Boyce-Codd Normal Form (BCNF) decomposition.
2. **Module 2: Transactional Escrow & Financial Isolation (`Escrow_Transactions`)**
   * Decouples active task bounties from general student wallet balances via an isolated financial ledger (`HELD`, `RELEASED`, `REFUNDED`).
   * Uses `sp_post_task_with_escrow` to atomically lock requester funds, deduct the bounty, create the task, and hold funds in escrow within a single ACID transaction.
3. **Module 3: High-Concurrency Bidding & Dispatch Engine (`Bids`)**
   * Prevents self-bidding rating manipulation via a dual-layer defense (`CHECK` constraint + `trg_prevent_self_bid` `BEFORE INSERT` trigger).
   * Automatically resolves competing bids upon runner assignment via the `trg_after_task_assignment` `AFTER UPDATE` trigger.
4. **Module 4: Cryptographic PIN Handover & Query Optimization (`Active_Open_Tasks_View`)**
   * Abstracts the live marketplace feed using `Active_Open_Tasks_View` so private `Verification_Pin` tokens are never exposed to browsing clients.
   * Executes atomic final settlement via `sp_complete_task_handover` upon 4-digit PIN verification.
   * Optimizes marketplace retrieval from $O(N)$ full-table scans to $O(\log N)$ B-Tree index lookups using composite indexing (`idx_tasks_status_id` and `idx_bids_composite`).

---

## 3. Relational Schema & Normalization Summary (BCNF)

| Relation | Primary Key | Candidate Keys | Functional Dependencies | Normal Form |
| :--- | :--- | :--- | :--- | :--- |
| **`Students`** | `Reg_No` | `Reg_No`, `Email` | `Reg_No` $\rightarrow$ `Name, Email, Trust_Rating, Balance`<br>`Email` $\rightarrow$ `Reg_No, Name, Trust_Rating, Balance` | **BCNF** |
| **`Tasks`** | `Task_ID` | `Task_ID` | `Task_ID` $\rightarrow$ `Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin, Created_At` | **BCNF** |
| **`Bids`** | `Bid_ID` | `Bid_ID`, `(Task_ID, Runner_ID)` | `Bid_ID` $\rightarrow$ `Task_ID, Runner_ID, Offered_Time, Bid_Status, Created_At`<br>`(Task_ID, Runner_ID)` $\rightarrow$ `Bid_ID, Offered_Time, Bid_Status, Created_At` | **BCNF** |
| **`Escrow_Transactions`** | `Txn_ID` | `Txn_ID`, `Task_ID` | `Txn_ID` $\rightarrow$ `Task_ID, Amount, Escrow_State, Released_At, Updated_At`<br>`Task_ID` $\rightarrow$ `Txn_ID, Amount, Escrow_State, Released_At, Updated_At` | **BCNF** |

* **1NF:** All attributes hold strictly atomic scalar values.
* **2NF:** Every non-prime attribute is fully functionally dependent on the entirety of every candidate key.
* **3NF:** Zero transitive dependencies ($X \rightarrow Y \rightarrow Z$) exist across any table.
* **BCNF:** For every non-trivial functional dependency $X \rightarrow Y$, the determinant $X$ is strictly a superkey.

---

## 4. Concurrency Control & Edge-Case Defense Matrix

| Concurrency Scenario | Failure Mode Without DBMS Guards | Relational Defense Mechanism Implemented |
| :--- | :--- | :--- |
| **Simultaneous Task Claiming** | Two runners claim the same errand at the exact same millisecond, causing duplicate assignment. | Pessimistic row-level exclusive lock (`SELECT ... FROM Tasks WHERE Task_ID = ? FOR UPDATE`) serializes concurrent transactions. |
| **Wallet Double-Spending** | A student rapidly submits multiple simultaneous task requests exceeding their wallet balance. | `SELECT Balance ... FOR UPDATE` inside `sp_post_task_with_escrow` locks the student row until deduction commits, backed by `CHECK (Balance >= 0.00)`. |
| **Runner Abandonment** | Assigned runner becomes unresponsive after accepting a task, locking requester funds indefinitely. | Automated timeout refund routine transitions `Escrow_State` to `'REFUNDED'` after `Offered_Time` expiry and restores `Students.Balance`. |
| **Self-Bidding Collusion** | A student bids on their own errand to artificially inflate their `Trust_Rating`. | Enforced via `chk_requester_runner_distinct` on `Tasks` and `trg_prevent_self_bid` on `Bids`. |

---

## 5. Repository Directory Structure

```text
campus-errand-dispatcher/
├── sql/                        # MySQL 8.0 DDL, Views, Indexes, Stored Procedures, and Triggers
├── src/                        # FastAPI + SQLAlchemy backend application layer
├── benchmarks/                 # Multi-threaded concurrency & index performance tests (for paper metrics)
├── paper/                      # Conference paper manuscript and architecture diagrams
├── docs/                       # Formal relational algebra & BCNF normalization proofs
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
