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
    requester_id: Optional[str] = Query(None, description="Filter tasks posted by this student"),
    runner_id: Optional[str] = Query(None, description="Filter tasks assigned to this runner"),
    db: Session = Depends(get_db)
):
    """
    Lists tasks with optional status and participant filtering.
    Enriched with requester and runner profile information and escrow status.
    """
    conditions = []
    params = {}

    if status_filter:
        conditions.append("t.Status = :status")
        params["status"] = status_filter
    if requester_id:
        conditions.append("t.Requester_ID = :requester_id")
        params["requester_id"] = requester_id
    if runner_id:
        conditions.append("t.Runner_ID = :runner_id")
        params["runner_id"] = runner_id

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    query_str = f"""
        SELECT 
            t.Task_ID, t.Requester_ID, t.Runner_ID, t.Pickup_Location, t.Drop_Location, 
            t.Bounty, t.Status, t.Verification_Pin, t.Created_At,
            req.Name AS Requester_Name, req.Trust_Rating AS Requester_Rating,
            run.Name AS Runner_Name, run.Trust_Rating AS Runner_Rating,
            e.Escrow_State, e.Amount AS Escrow_Amount
        FROM Tasks t
        JOIN Students req ON t.Requester_ID = req.Reg_No
        LEFT JOIN Students run ON t.Runner_ID = run.Reg_No
        LEFT JOIN Escrow_Transactions e ON t.Task_ID = e.Task_ID
        {where_clause}
        ORDER BY t.Task_ID DESC
    """
    rows = db.execute(text(query_str), params).mappings().all()

    return [
        {
            "task_id": row["Task_ID"],
            "requester_id": row["Requester_ID"],
            "requester_name": row["Requester_Name"],
            "requester_rating": float(row["Requester_Rating"]) if row["Requester_Rating"] else None,
            "runner_id": row["Runner_ID"],
            "runner_name": row["Runner_Name"],
            "runner_rating": float(row["Runner_Rating"]) if row["Runner_Rating"] else None,
            "pickup_location": row["Pickup_Location"],
            "drop_location": row["Drop_Location"],
            "bounty": float(row["Bounty"]),
            "status": row["Status"],
            "verification_pin": row["Verification_Pin"],
            "escrow_state": row["Escrow_State"],
            "escrow_amount": float(row["Escrow_Amount"]) if row["Escrow_Amount"] else None,
            "created_at": row["Created_At"].isoformat() if row["Created_At"] else None
        }
        for row in rows
    ]



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


@router.get("/tasks/{task_id}")
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """Fetches comprehensive details for a specific task."""
    query = text("""
        SELECT 
            t.Task_ID, t.Requester_ID, t.Runner_ID, t.Pickup_Location, t.Drop_Location, 
            t.Bounty, t.Status, t.Verification_Pin, t.Created_At,
            req.Name AS Requester_Name, req.Trust_Rating AS Requester_Rating, req.Email AS Requester_Email,
            run.Name AS Runner_Name, run.Trust_Rating AS Runner_Rating, run.Email AS Runner_Email,
            e.Txn_ID, e.Escrow_State, e.Amount AS Escrow_Amount, e.Released_At, e.Updated_At AS Escrow_Updated_At
        FROM Tasks t
        JOIN Students req ON t.Requester_ID = req.Reg_No
        LEFT JOIN Students run ON t.Runner_ID = run.Reg_No
        LEFT JOIN Escrow_Transactions e ON t.Task_ID = e.Task_ID
        WHERE t.Task_ID = :task_id
    """)
    row = db.execute(query, {"task_id": task_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    return {
        "task_id": row["Task_ID"],
        "requester_id": row["Requester_ID"],
        "requester_name": row["Requester_Name"],
        "requester_email": row["Requester_Email"],
        "requester_rating": float(row["Requester_Rating"]) if row["Requester_Rating"] else None,
        "runner_id": row["Runner_ID"],
        "runner_name": row["Runner_Name"],
        "runner_email": row["Runner_Email"],
        "runner_rating": float(row["Runner_Rating"]) if row["Runner_Rating"] else None,
        "pickup_location": row["Pickup_Location"],
        "drop_location": row["Drop_Location"],
        "bounty": float(row["Bounty"]),
        "status": row["Status"],
        "verification_pin": row["Verification_Pin"],
        "created_at": row["Created_At"].isoformat() if row["Created_At"] else None,
        "escrow": {
            "txn_id": row["Txn_ID"],
            "state": row["Escrow_State"],
            "amount": float(row["Escrow_Amount"]) if row["Escrow_Amount"] else None,
            "released_at": row["Released_At"].isoformat() if row["Released_At"] else None,
            "updated_at": row["Escrow_Updated_At"].isoformat() if row["Escrow_Updated_At"] else None
        } if row["Txn_ID"] else None
    }


@router.post("/tasks/{task_id}/cancel")
def cancel_and_refund_task(task_id: int, db: Session = Depends(get_db)):
    """
    Cancels an unfulfilled or abandoned task and refunds the locked escrow bounty back to requester.
    Executes sp_refund_abandoned_task within MySQL.
    """
    call_sp = text("CALL sp_refund_abandoned_task(:task_id)")
    try:
        db.execute(call_sp, {"task_id": task_id})
        db.commit()
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=extract_db_error_message(e))

    return {"message": f"Task #{task_id} successfully cancelled and escrow funds refunded to requester."}

