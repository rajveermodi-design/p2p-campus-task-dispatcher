from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from src.database import get_db
from src.schemas import (
    StudentCreate,
    StudentResponse,
    TaskCreate,
    TaskFeedResponse,
    TaskHandoverVerify,
    BidCreate,
    BidResponse,
)

app = FastAPI(
    title="Peer-to-Peer Campus Errand Dispatcher API",
    description="High-concurrency, ACID-compliant errand dispatch system with escrow isolation.",
    version="1.0.0"
)

# Enable CORS for frontend/mobile clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_db_error_message(e: DBAPIError) -> str:
    """Helper to extract clean custom SIGNAL messages from MySQL 45000 errors."""
    if hasattr(e, "orig") and hasattr(e.orig, "args") and len(e.orig.args) > 1:
        return str(e.orig.args[1])
    return str(e)


# ============================================================================
# 1. SYSTEM & HEALTH CHECK
# ============================================================================

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "Campus Errand Dispatcher",
        "engine": "MySQL 8.0 InnoDB",
        "docs_url": "/docs"
    }


# ============================================================================
# 2. STUDENT ACCOUNTS
# ============================================================================

@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Registers a new campus participant subject to institutional domain constraints."""
    query = text("""
        INSERT INTO Students (Reg_No, Name, Email, Balance, Trust_Rating)
        VALUES (:reg_no, :name, :email, 0.00, 5.00)
    """)
    try:
        db.execute(query, {
            "reg_no": student.reg_no,
            "name": student.name,
            "email": student.email
        })
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student registration number or institutional email already registered."
        )
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extract_db_error_message(e)
        )

    # Fetch newly created student
    result = db.execute(
        text("SELECT Reg_No, Name, Email, Trust_Rating, Balance, Created_At FROM Students WHERE Reg_No = :reg_no"),
        {"reg_no": student.reg_no}
    ).mappings().first()

    return {
        "reg_no": result["Reg_No"],
        "name": result["Name"],
        "email": result["Email"],
        "trust_rating": result["Trust_Rating"],
        "balance": result["Balance"],
        "created_at": result["Created_At"]
    }


@app.get("/students/{reg_no}", response_model=StudentResponse, tags=["Students"])
def get_student_profile(reg_no: str, db: Session = Depends(get_db)):
    """Fetches a student's public profile, rating, and wallet balance."""
    result = db.execute(
        text("SELECT Reg_No, Name, Email, Trust_Rating, Balance, Created_At FROM Students WHERE Reg_No = :reg_no"),
        {"reg_no": reg_no.upper()}
    ).mappings().first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    return {
        "reg_no": result["Reg_No"],
        "name": result["Name"],
        "email": result["Email"],
        "trust_rating": result["Trust_Rating"],
        "balance": result["Balance"],
        "created_at": result["Created_At"]
    }


# ============================================================================
# 3. TASK MARKETPLACE (ESCROW & PRIVACY ABSTRACTIONS)
# ============================================================================

@app.get("/tasks/feed", response_model=List[TaskFeedResponse], tags=["Marketplace Feed"])
def get_marketplace_feed(db: Session = Depends(get_db)):
    """
    Returns public open tasks from the Active_Open_Tasks_View.
    Sensitive tokens (Verification PIN, requester balance) are omitted.
    """
    query = text("""
        SELECT Task_ID, Pickup_Location, Drop_Location, Bounty, Requester_Name, Requester_Rating, Created_At
        FROM Active_Open_Tasks_View
        ORDER BY Created_At DESC
    """)
    rows = db.execute(query).mappings().all()

    return [
        {
            "task_id": row["Task_ID"],
            "pickup_location": row["Pickup_Location"],
            "drop_location": row["Drop_Location"],
            "bounty": row["Bounty"],
            "requester_name": row["Requester_Name"],
            "requester_rating": row["Requester_Rating"],
            "created_at": row["Created_At"]
        }
        for row in rows
    ]


@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Marketplace Feed"])
def create_task_with_escrow(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Atomically posts an errand and freezes bounty into escrow via sp_post_task_with_escrow.
    """
    call_sp = text("""
        CALL sp_post_task_with_escrow(
            :requester_id,
            :pickup_location,
            :drop_location,
            :bounty,
            :verification_pin
        )
    """)
    try:
        db.execute(call_sp, {
            "requester_id": task.requester_id,
            "pickup_location": task.pickup_location,
            "drop_location": task.drop_location,
            "bounty": float(task.bounty),
            "verification_pin": task.verification_pin
        })
        db.commit()
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extract_db_error_message(e)
        )

    return {"message": "Task created successfully and bounty held in escrow."}


# ============================================================================
# 4. BIDDING SYSTEM
# ============================================================================

@app.post("/tasks/{task_id}/bids", status_code=status.HTTP_201_CREATED, tags=["Bids"])
def place_bid(task_id: int, bid: BidCreate, db: Session = Depends(get_db)):
    """
    Submits a competitive bid.
    Fails if the runner attempts to self-bid (enforced by trg_prevent_self_bid).
    """
    query = text("""
        INSERT INTO Bids (Task_ID, Runner_ID, Offered_Time, Bid_Status)
        VALUES (:task_id, :runner_id, CURRENT_TIMESTAMP, 'pending')
    """)
    try:
        db.execute(query, {
            "task_id": task_id,
            "runner_id": bid.runner_id
        })
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate bid: Runner has already placed an active bid on this errand."
        )
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extract_db_error_message(e)
        )

    return {"message": "Bid submitted successfully."}


@app.post("/tasks/{task_id}/assign", tags=["Bids"])
def assign_runner(task_id: int, runner_id: str, db: Session = Depends(get_db)):
    """
    Assigns a runner to the task.
    Triggers trg_after_task_assignment to accept the winning bid and reject competing bids.
    """
    # 1. Verify task is in 'open' status
    task_row = db.execute(
        text("SELECT Status FROM Tasks WHERE Task_ID = :task_id"),
        {"task_id": task_id}
    ).mappings().first()

    if not task_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    if task_row["Status"] != "open":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task is not open for assignment.")

    # 2. Verify the chosen runner has an active bid
    bid_row = db.execute(
        text("SELECT Bid_ID FROM Bids WHERE Task_ID = :task_id AND Runner_ID = :runner_id"),
        {"task_id": task_id, "runner_id": runner_id}
    ).mappings().first()

    if not bid_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching bid found for this runner.")

    # 3. Update task (Fires trg_after_task_assignment)
    update_task = text("""
        UPDATE Tasks
        SET Runner_ID = :runner_id, Status = 'assigned'
        WHERE Task_ID = :task_id
    """)
    try:
        db.execute(update_task, {"task_id": task_id, "runner_id": runner_id})
        db.commit()
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=extract_db_error_message(e))

    return {"message": f"Runner {runner_id} assigned successfully. Competing bids resolved automatically."}


# ============================================================================
# 5. HANDOVER VERIFICATION & ESCROW RELEASE
# ============================================================================

@app.post("/tasks/{task_id}/complete", tags=["Handover & Payout"])
def verify_and_complete_task(task_id: int, payload: TaskHandoverVerify, db: Session = Depends(get_db)):
    """
    Completes task handover and releases escrow balance to runner via sp_complete_task_handover.
    """
    call_sp = text("""
        CALL sp_complete_task_handover(
            :task_id,
            :runner_id,
            :pin
        )
    """)
    try:
        db.execute(call_sp, {
            "task_id": task_id,
            "runner_id": payload.runner_id,
            "pin": payload.verification_pin
        })
        db.commit()
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extract_db_error_message(e)
        )

    return {"message": "Verification PIN confirmed! Escrow funds released to runner wallet."}