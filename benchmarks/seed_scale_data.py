import random
from sqlalchemy import text
from src.database import engine

TOTAL_TASKS = 10000
CHUNK_SIZE = 1000

STUDENTS = ["25BCE0750", "25BCE0724", "25BCE0717", "25BCE1002", "25BCE1003"]
LOCATIONS = [
    "Food Mall Ground Floor", "Technology Tower (TT) 412",
    "SJT 3rd Floor Lab", "PRP Block Entrance",
    "Main Library Gate", "Darling Bakery",
    "Gymkhana Ground", "Gazebo Food Court"
]

# Real-world distribution: 85% completed, 10% cancelled, 5% open
STATUS_POOL = ["completed"] * 85 + ["cancelled"] * 10 + ["open"] * 5


def seed_scale_dataset():
    print("=" * 75)
    print(f"GENERATING PRODUCTION SCALE DATASET ({TOTAL_TASKS:,} TASKS & BIDS)")
    print("=" * 75)

    with engine.begin() as conn:
        # 1. Clean out any previous synthetic scale runs to keep seed data pristine
        print("[*] Purging prior synthetic benchmark data (preserving base seeds 1-3)...")
        conn.execute(text("DELETE FROM Bids WHERE Task_ID > 3"))
        conn.execute(text("DELETE FROM Tasks WHERE Task_ID > 3"))

        # 2. Generate 10,000 synthetic tasks in memory
        print("[*] Generating 10,000 synthetic tasks in batches...")
        task_rows = []
        for _ in range(TOTAL_TASKS):
            status = random.choice(STATUS_POOL)
            req = random.choice(STUDENTS)
            avail_runners = [s for s in STUDENTS if s != req]
            runner = random.choice(avail_runners) if status != "open" else None

            task_rows.append({
                "req": req,
                "runner": runner,
                "pickup": random.choice(LOCATIONS),
                "drop": random.choice(LOCATIONS),
                "bounty": round(random.uniform(20.0, 150.0), 2),
                "pin": f"{random.randint(1000, 9999)}",
                "status": status
            })

            if len(task_rows) >= CHUNK_SIZE:
                conn.execute(text("""
                    INSERT INTO Tasks (Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Verification_Pin, Status)
                    VALUES (:req, :runner, :pickup, :drop, :bounty, :pin, :status)
                """), task_rows)
                task_rows.clear()

        if task_rows:
            conn.execute(text("""
                INSERT INTO Tasks (Requester_ID, Runner_ID, Pickup_Location, Drop_Location, Bounty, Verification_Pin, Status)
                VALUES (:req, :runner, :pickup, :drop, :bounty, :pin, :status)
            """), task_rows)

        # 3. Retrieve Task_ID alongside Requester_ID to prevent self-bidding
        print("[*] Fetching metadata to generate compliant bids...")
        tasks_meta = conn.execute(
            text("SELECT Task_ID, Requester_ID FROM Tasks WHERE Task_ID > 3 ORDER BY Task_ID ASC")
        ).mappings().all()

        print("[*] Generating 10,000 synthetic bids (strictly filtering out self-bids)...")
        bid_rows = []
        bid_status_pool = ["rejected"] * 80 + ["accepted"] * 15 + ["pending"] * 5

        for row in tasks_meta:
            tid = row["Task_ID"]
            req = row["Requester_ID"]
            # Exclude the requester so the trigger is never violated
            eligible_bidders = [s for s in STUDENTS if s != req]

            bid_rows.append({
                "tid": tid,
                "runner": random.choice(eligible_bidders),
                "status": random.choice(bid_status_pool)
            })

            if len(bid_rows) >= CHUNK_SIZE:
                conn.execute(text("""
                    INSERT INTO Bids (Task_ID, Runner_ID, Offered_Time, Bid_Status)
                    VALUES (:tid, :runner, CURRENT_TIMESTAMP, :status)
                """), bid_rows)
                bid_rows.clear()

        if bid_rows:
            conn.execute(text("""
                INSERT INTO Bids (Task_ID, Runner_ID, Offered_Time, Bid_Status)
                VALUES (:tid, :runner, CURRENT_TIMESTAMP, :status)
            """), bid_rows)

    print("[SUCCESS] Production dataset injected into MySQL successfully.")


if __name__ == "__main__":
    seed_scale_dataset()