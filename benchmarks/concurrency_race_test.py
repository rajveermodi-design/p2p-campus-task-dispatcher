import concurrent.futures
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

# Target errand from seed data
TASK_ID = 1

# Student runners competing in the simulation
BIDDING_RUNNERS = [
    "25BCE0724",  # Yajas
    "25BCE0717",  # Abhayadev
    "25BCE1002",  # Karthik
    "25BCE1003",  # Rohan
]


def test_concurrent_bids():
    """Fires simultaneous bids to test index lookups and duplicate-prevention constraints."""
    print("\n" + "=" * 70)
    print("BENCHMARK 1: SIMULTANEOUS RUNNER BIDS (HIGH CONTENTION)")
    print("=" * 70)

    def submit_bid(runner_id: str):
        url = f"{BASE_URL}/tasks/{TASK_ID}/bids"
        payload = {"task_id": TASK_ID, "runner_id": runner_id}
        start = time.perf_counter()
        res = requests.post(url, json=payload)
        elapsed = (time.perf_counter() - start) * 1000
        return runner_id, res.status_code, res.json(), elapsed

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(BIDDING_RUNNERS)) as pool:
        results = list(pool.map(submit_bid, BIDDING_RUNNERS))

    print(f"{'Runner ID':<15} | {'HTTP Code':<10} | {'Latency (ms)':<15} | {'Server Response'}")
    print("-" * 70)
    for runner_id, code, body, lat in results:
        msg = body.get("message") or body.get("detail")
        print(f"{runner_id:<15} | {code:<10} | {lat:<15.2f} | {msg}")


def test_double_spending_race():
    """
    Fires 2 parallel completion attempts with the exact same valid PIN.
    Tests InnoDB row-level locking (SELECT ... FOR UPDATE) in sp_complete_task_handover.
    """
    print("\n" + "=" * 70)
    print("BENCHMARK 2: DOUBLE-SPENDING RACE CONDITION (ESCROW PAYOUT)")
    print("=" * 70)

    # First assign the runner if not already assigned
    assign_url = f"{BASE_URL}/tasks/{TASK_ID}/assign"
    requests.post(assign_url, params={"runner_id": "25BCE0724"})

    def claim_payout(thread_name: str):
        url = f"{BASE_URL}/tasks/{TASK_ID}/complete"
        payload = {"runner_id": "25BCE0724", "verification_pin": "4821"}
        start = time.perf_counter()
        res = requests.post(url, json=payload)
        elapsed = (time.perf_counter() - start) * 1000
        return thread_name, res.status_code, res.json(), elapsed

    threads = ["Thread-Alpha", "Thread-Beta"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(claim_payout, threads))

    print(f"{'Execution Thread':<18} | {'HTTP Code':<10} | {'Latency (ms)':<15} | {'Server Response'}")
    print("-" * 70)
    for thread, code, body, lat in results:
        msg = body.get("message") or body.get("detail")
        print(f"{thread:<18} | {code:<10} | {lat:<15.2f} | {msg}")


if __name__ == "__main__":
    test_concurrent_bids()
    test_double_spending_race()