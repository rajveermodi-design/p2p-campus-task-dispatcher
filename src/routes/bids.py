from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from src.database import get_db
from src.schemas import BidCreate

router = APIRouter(tags=["Bids"])


def extract_db_error_message(e: DBAPIError) -> str:
    """Helper to extract clean custom SIGNAL messages from MySQL 45000 errors."""
    if hasattr(e, "orig") and hasattr(e.orig, "args") and len(e.orig.args) > 1:
        return str(e.orig.args[1])
    return str(e)


@router.post("/tasks/{task_id}/bids", status_code=status.HTTP_201_CREATED)
def place_bid(task_id: int, bid: BidCreate, db: Session = Depends(get_db)):
    """
    Submits a competitive bid.
    Catches MySQL duplicate key error (1062) and maps to HTTP 409 Conflict.
    Catches trigger self-bid exception (1644 / SQLSTATE 45000) and maps to HTTP 400 Bad Request.
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
    except IntegrityError:
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


@router.get("/tasks/{task_id}/bids")
def get_task_bids(task_id: int, db: Session = Depends(get_db)):
    """
    Returns all bids placed on a task, joined with Runner name and trust rating.
    """
    query = text("""
        SELECT b.Bid_ID, b.Task_ID, b.Runner_ID, s.Name AS Runner_Name, s.Trust_Rating AS Runner_Rating,
               b.Offered_Time, b.Bid_Status, b.Created_At
        FROM Bids b
        JOIN Students s ON b.Runner_ID = s.Reg_No
        WHERE b.Task_ID = :task_id
        ORDER BY b.Offered_Time DESC
    """)
    rows = db.execute(query, {"task_id": task_id}).mappings().all()

    return [
        {
            "bid_id": row["Bid_ID"],
            "task_id": row["Task_ID"],
            "runner_id": row["Runner_ID"],
            "runner_name": row["Runner_Name"],
            "runner_rating": float(row["Runner_Rating"]),
            "offered_time": row["Offered_Time"].isoformat() if row["Offered_Time"] else None,
            "bid_status": row["Bid_Status"],
            "created_at": row["Created_At"].isoformat() if row["Created_At"] else None
        }
        for row in rows
    ]

