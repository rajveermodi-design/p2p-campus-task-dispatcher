from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from src.database import get_db

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """Computes aggregate analytics and real-time ACID transaction metrics."""
    try:
        tasks_count = db.execute(text("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN Status = 'open' THEN 1 ELSE 0 END) AS open_count,
                SUM(CASE WHEN Status = 'assigned' THEN 1 ELSE 0 END) AS assigned_count,
                SUM(CASE WHEN Status = 'completed' THEN 1 ELSE 0 END) AS completed_count,
                SUM(CASE WHEN Status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count,
                COALESCE(SUM(Bounty), 0.00) AS total_bounty_volume
            FROM Tasks
        """)).mappings().first()

        students_count = db.execute(text("""
            SELECT 
                COUNT(*) AS total_students,
                COALESCE(AVG(Trust_Rating), 5.0) AS avg_rating,
                COALESCE(SUM(Balance), 0.00) AS total_wallet_balance
            FROM Students
        """)).mappings().first()

        escrow_stats = db.execute(text("""
            SELECT 
                COALESCE(SUM(CASE WHEN Escrow_State = 'HELD' THEN Amount ELSE 0 END), 0.00) AS held_amount,
                COALESCE(SUM(CASE WHEN Escrow_State = 'RELEASED' THEN Amount ELSE 0 END), 0.00) AS released_amount,
                COALESCE(SUM(CASE WHEN Escrow_State = 'REFUNDED' THEN Amount ELSE 0 END), 0.00) AS refunded_amount
            FROM Escrow_Transactions
        """)).mappings().first()

        bids_count = db.execute(text("SELECT COUNT(*) AS total_bids FROM Bids")).scalar()

        return {
            "tasks": {
                "total": tasks_count["total"] or 0,
                "open": tasks_count["open_count"] or 0,
                "assigned": tasks_count["assigned_count"] or 0,
                "completed": tasks_count["completed_count"] or 0,
                "cancelled": tasks_count["cancelled_count"] or 0,
                "total_volume": float(tasks_count["total_bounty_volume"] or 0.0)
            },
            "students": {
                "total": students_count["total_students"] or 0,
                "avg_rating": round(float(students_count["avg_rating"] or 5.0), 2),
                "total_wallet": float(students_count["total_wallet_balance"] or 0.0)
            },
            "escrow": {
                "held": float(escrow_stats["held_amount"] or 0.0),
                "released": float(escrow_stats["released_amount"] or 0.0),
                "refunded": float(escrow_stats["refunded_amount"] or 0.0)
            },
            "bids": {
                "total": bids_count or 0
            }
        }
    except DBAPIError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset")
def reset_demo_database(db: Session = Depends(get_db)):
    """
    Restores the database to its pristine demo state.
    Re-seeds baseline students, active errands, escrow balances, and bids.
    """
    try:
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        db.execute(text("DELETE FROM Escrow_Transactions"))
        db.execute(text("DELETE FROM Bids"))
        db.execute(text("DELETE FROM Tasks"))
        db.execute(text("DELETE FROM Students"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

        # Re-seed Students
        db.execute(text("""
            INSERT INTO Students (Reg_No, Name, Email, Trust_Rating, Balance) VALUES
            ('25BCE0750', 'Rajveer Modi',       'rajveer.modi2025@vitstudent.ac.in',    4.95, 1250.00),
            ('25BCE0724', 'Yajas AB',           'yajas.ab2025@vitstudent.ac.in',        4.80,  850.00),
            ('25BCE0717', 'Abhayadev RVM',      'abhayadev.rvm2025@vitstudent.ac.in',   4.90,  620.00),
            ('25BCE1001', 'Ananya Sharma',      'ananya.sharma2025@vitstudent.ac.in',   4.65,  300.00),
            ('25BCE1002', 'Karthik Raman',      'karthik.raman2025@vitstudent.ac.in',   4.20,  150.00),
            ('25BCE1003', 'Rohan Verma',        'rohan.verma2025@vitstudent.ac.in',     3.80,    0.00);
        """))

        # Re-seed Tasks & Escrow
        db.execute(text("""
            INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
            VALUES (1, '25BCE0750', NULL, 'Food Mall Ground Floor', 'Technology Tower (TT) 412', 60.00, 'open', '4821');
        """))
        db.execute(text("""
            INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
            VALUES (1, 1, 60.00, 'HELD', NULL);
        """))

        db.execute(text("""
            INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
            VALUES (2, '25BCE0724', '25BCE0717', 'Main Library Reprography', 'SJT Block 3rd Floor Lab', 40.00, 'assigned', '9103');
        """))
        db.execute(text("""
            INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
            VALUES (2, 2, 40.00, 'HELD', NULL);
        """))

        db.execute(text("""
            INSERT INTO Tasks (Task_ID, Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Status, Verification_Pin)
            VALUES (3, '25BCE1001', '25BCE1002', 'Men''s Hostel Block D', 'Men''s Hostel Block L 204', 50.00, 'completed', '3378');
        """))
        db.execute(text("""
            INSERT INTO Escrow_Transactions (Txn_ID, Task_ID, Amount, Escrow_State, Released_At)
            VALUES (3, 3, 50.00, 'RELEASED', CURRENT_TIMESTAMP);
        """))

        # Re-seed Bids
        db.execute(text("""
            INSERT INTO Bids (Bid_ID, Task_ID, Runner_ID, Offered_Time, Bid_Status) VALUES
            (1, 1, '25BCE0724', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 20 MINUTE), 'pending'),
            (2, 1, '25BCE0717', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 10 MINUTE), 'pending'),
            (3, 2, '25BCE0717', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 45 MINUTE), 'accepted'),
            (4, 2, '25BCE1002', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 35 MINUTE), 'rejected'),
            (5, 3, '25BCE1002', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 90 MINUTE), 'accepted');
        """))

        db.commit()
        return {"message": "Database reset to pristine baseline demo state."}
    except DBAPIError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/landmarks")
def get_campus_landmarks():
    """Returns curated campus nodes for the Air Traffic Control Radar visualization."""
    return [
        {"id": "food_mall", "name": "Food Mall Ground Floor", "short": "Food Mall", "x": 28, "y": 68, "type": "hub"},
        {"id": "tt", "name": "Technology Tower (TT) 412", "short": "Tech Tower (TT)", "x": 76, "y": 32, "type": "academic"},
        {"id": "library", "name": "Main Library Reprography", "short": "Main Library", "x": 48, "y": 42, "type": "library"},
        {"id": "sjt", "name": "SJT Block 3rd Floor Lab", "short": "SJT Block", "x": 82, "y": 66, "type": "academic"},
        {"id": "hostel_d", "name": "Men's Hostel Block D", "short": "Hostel Block D", "x": 18, "y": 28, "type": "hostel"},
        {"id": "hostel_l", "name": "Men's Hostel Block L 204", "short": "Hostel Block L", "x": 22, "y": 52, "type": "hostel"},
        {"id": "ladies_hostel", "name": "Ladies Hostel Block A", "short": "Ladies Hostel", "x": 62, "y": 82, "type": "hostel"},
        {"id": "mb", "name": "MB Ground Reprographics", "short": "Main Building (MB)", "x": 52, "y": 18, "type": "academic"},
        {"id": "prp", "name": "PRP Building Lounge", "short": "PRP Center", "x": 38, "y": 85, "type": "academic"}
    ]
