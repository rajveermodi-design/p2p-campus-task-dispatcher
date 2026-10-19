from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from src.database import get_db
from src.schemas import TaskCreate, TaskFeedResponse, TaskHandoverVerify

router = APIRouter(tags=["Tasks"])


def extract_db_error_message(e: DBAPIError) -> str:
    """Helper to extract clean custom SIGNAL messages from MySQL 45000 errors."""
    if hasattr(e, "orig") and hasattr(e.orig, "args") and len(e.orig.args) > 1:
        return str(e.orig.args[1])
    return str(e)


@router.get("/tasks/feed", response_model=List[TaskFeedResponse])
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


@router.get("/tasks")
def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter tasks by status, utilizes idx_tasks_status_id"),
    db: Session = Depends(get_db)
):
    """
    Lists tasks with optional status filtering.
    When status is supplied (e.g., 'open'), utilizes composite index idx_tasks_status_id.
    """
    if status_filter:
        query = text("""
            SELECT Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Created_At
            FROM Tasks
            WHERE Status = :status
            ORDER BY Task_ID DESC
        """)
        rows = db.execute(query, {"status": status_filter}).mappings().all()
    else:
        query = text("""
            SELECT Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Created_At
            FROM Tasks
            ORDER BY Task_ID DESC
        """)
        rows = db.execute(query).mappings().all()

    return [dict(row) for row in rows]


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task_with_escrow(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Atomically posts an errand and freezes bounty into escrow via sp_post_task_with_escrow.
    Validates requester balance prior to insertion within the stored procedure.
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


@router.post("/tasks/{task_id}/assign")
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


@router.post("/tasks/{task_id}/complete")
def verify_and_complete_task(task_id: int, payload: TaskHandoverVerify, db: Session = Depends(get_db)):
    """
    Completes task handover and releases escrow balance to runner via sp_complete_task_handover.
    Catches MySQL 1644 / SQLSTATE 45000 and maps to HTTP 400 Bad Request.
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
