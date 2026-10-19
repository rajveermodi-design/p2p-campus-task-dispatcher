import concurrent.futures
import time
import requests

BASE_URL = "http://127.0.0.1:8000"
TASK_ID = 1
RUNNER_ID = "25BCE0724"
VALID_PIN = "4821"
CONCURRENT_ATTEMPTS = 10


def get_runner_balance(runner_id: str) -> float:
    """Fetches current student wallet balance."""
    res = requests.get(f"{BASE_URL}/students/{runner_id}")
    if res.status_code == 200:
        return float(res.json()["balance"])
    raise RuntimeError(f"Could not fetch student {runner_id}: {res.text}")


def execute_payout_claim(thread_id: int):
    """Sends a single payout completion request."""
    url = f"{BASE_URL}/tasks/{TASK_ID}/complete"
    payload = {"runner_id": RUNNER_ID, "verification_pin": VALID_PIN}
    start = time.perf_counter()
    res = requests.post(url, json=payload)
    elapsed = (time.perf_counter() - start) * 1000
    return thread_id, res.status_code, res.json(), elapsed


def run_double_spend_benchmark():
    print("=" * 75)
    print("STRESS BENCHMARK: HIGH-VOLUME DOUBLE-SPEND ATTACK (10 PARALLEL THREADS)")
    print("=" * 75)

    # 1. Capture pre-test balance
    initial_balance = get_runner_balance(RUNNER_ID)
    print(f"[*] Pre-Attack Balance for Runner {RUNNER_ID}: Rs. {initial_balance:.2f}")
    print(f"[*] Launching {CONCURRENT_ATTEMPTS} simultaneous claims for Task #{TASK_ID}...")

    # 2. Fire 10 parallel threads simultaneously
    start_all = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_ATTEMPTS) as pool:
        futures = [pool.submit(execute_payout_claim, i + 1) for i in range(CONCURRENT_ATTEMPTS)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    total_time = (time.perf_counter() - start_all) * 1000

    # 3. Analyze HTTP responses
    success_count = sum(1 for _, code, _, _ in results if code == 200)
    rejected_count = sum(1 for _, code, _, _ in results if code == 400)

    print("\n" + f"{'Thread':<12} | {'HTTP Code':<10} | {'Latency (ms)':<15} | {'Server Message'}")
    print("-" * 75)
    for tid, code, body, lat in sorted(results, key=lambda x: x[0]):
        msg = body.get("message") or body.get("detail")
        print(f"Thread #{tid:<5} | {code:<10} | {lat:<15.2f} | {msg}")

    # 4. Capture post-test balance and verify mathematical invariant
    final_balance = get_runner_balance(RUNNER_ID)
    net_credited = final_balance - initial_balance

    print("\n" + "=" * 75)
    print("AUDIT & BALANCE INVARIANT VERIFICATION")
    print("=" * 75)
    print(f"Total Parallel Requests : {CONCURRENT_ATTEMPTS}")
    print(f"Successful Payouts      : {success_count} (Expected: 1)")
    print(f"Rejected Rogue Claims   : {rejected_count} (Expected: {CONCURRENT_ATTEMPTS - 1})")
    print(f"Total Execution Time    : {total_time:.2f} ms")
    print(f"Initial Runner Balance  : Rs. {initial_balance:.2f}")
    print(f"Final Runner Balance    : Rs. {final_balance:.2f}")
    print(f"Net Amount Disbursed    : Rs. {net_credited:.2f}")

    if success_count == 1 and rejected_count == (CONCURRENT_ATTEMPTS - 1):
        print("\n[VERDICT: PASS] ACID isolation held. Zero double-spending detected.")
    else:
        print("\n[VERDICT: FAIL] Financial invariant violated! Escrow was leaked.")


if __name__ == "__main__":
    run_double_spend_benchmark()