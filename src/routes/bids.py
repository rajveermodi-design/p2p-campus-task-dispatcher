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
