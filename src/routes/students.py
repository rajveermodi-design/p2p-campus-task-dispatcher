from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from src.database import get_db
from src.schemas import StudentCreate, StudentResponse

router = APIRouter(tags=["Students"])


def extract_db_error_message(e: DBAPIError) -> str:
    """Helper to extract clean custom SIGNAL messages from MySQL 45000 errors."""
    if hasattr(e, "orig") and hasattr(e.orig, "args") and len(e.orig.args) > 1:
        return str(e.orig.args[1])
    return str(e)


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
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
    except IntegrityError:
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


@router.get("/students/{reg_no}", response_model=StudentResponse)
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
