import time
import statistics
from sqlalchemy import text
from src.database import engine

ITERATIONS = 500


def benchmark_query(conn, query_str: str, label: str):
    """Executes a query repeatedly to compute empirical latency percentiles."""
    latencies = []
    
    # Warm-up pass to populate database buffer pools
    for _ in range(20):
        conn.execute(text(query_str))

    for _ in range(ITERATIONS):
        t0 = time.perf_counter()
        conn.execute(text(query_str))
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    avg_lat = statistics.mean(latencies)
    p95_lat = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    return avg_lat, p95_lat


def run_index_benchmark():
    print("=" * 80)
    print("BENCHMARK: COMPOSITE B-TREE INDEX VS FULL TABLE SCAN")
    print(f"Sampling iterations: {ITERATIONS} queries per scenario")
    print("=" * 80)

    with engine.connect() as conn:
        # 1. Query Execution Plan Analysis via EXPLAIN (Explicitly TRADITIONAL format)
        print("\n[1] QUERY PLAN COST EVALUATION (EXPLAIN):")
        
        # Explicit FORMAT=TRADITIONAL ensures compatibility across MySQL 8.0, 8.4+, and 9.0
        explain_indexed = conn.execute(
            text("EXPLAIN FORMAT=TRADITIONAL SELECT Task_ID, Pickup_Location, Bounty FROM Tasks WHERE Status = 'open'")
        ).mappings().first()
        
        explain_unindexed = conn.execute(
            text("EXPLAIN FORMAT=TRADITIONAL SELECT Task_ID, Pickup_Location, Bounty FROM Tasks IGNORE INDEX (idx_tasks_status_id) WHERE Status = 'open'")
        ).mappings().first()

        # Normalize column dictionary keys to lowercase for driver safety
        exp_idx = {str(k).lower(): v for k, v in explain_indexed.items()}
        exp_unidx = {str(k).lower(): v for k, v in explain_unindexed.items()}

        idx_type = exp_idx.get("type", "ref")
        idx_key = exp_idx.get("key", "idx_tasks_status_id")
        idx_rows = exp_idx.get("rows", 1)

        unidx_type = exp_unidx.get("type", "ALL")
        unidx_key = str(exp_unidx.get("key", "None"))
        unidx_rows = exp_unidx.get("rows", 1)

        print(f"  * Indexed Plan   -> Access Type: {idx_type:<6} | Key Used: {idx_key:<20} | Est. Rows Scanned: {idx_rows}")
        print(f"  * Unindexed Plan -> Access Type: {unidx_type:<6} | Key Used: {unidx_key:<20} | Est. Rows Scanned: {unidx_rows}")

        # 2. Latency Benchmarking on Active Feed Lookups
        print("\n[2] RUNTIME PERFORMANCE BENCHMARKING (MARKETPLACE FEED):")
        
        q_indexed = "SELECT Task_ID, Pickup_Location, Bounty FROM Tasks WHERE Status = 'open'"
        q_unindexed = "SELECT Task_ID, Pickup_Location, Bounty FROM Tasks IGNORE INDEX (idx_tasks_status_id) WHERE Status = 'open'"

        idx_avg, idx_p95 = benchmark_query(conn, q_indexed, "Indexed")
        no_idx_avg, no_idx_p95 = benchmark_query(conn, q_unindexed, "Unindexed")

        speedup = ((no_idx_avg - idx_avg) / no_idx_avg) * 100 if no_idx_avg > 0 else 0

        print(f"{'Execution Strategy':<28} | {'Mean Latency (ms)':<20} | {'P95 Latency (ms)':<20}")
        print("-" * 80)
        print(f"{'Using idx_tasks_status_id':<28} | {idx_avg:<20.4f} | {idx_p95:<20.4f}")
        print(f"{'Table Scan (IGNORE INDEX)':<28} | {no_idx_avg:<20.4f} | {no_idx_p95:<20.4f}")
        print("-" * 80)
        print(f"Efficiency Gain: Composite B-Tree achieves a {speedup:.1f}% reduction in mean query overhead.")

        # 3. Runner Bid Lookups Benchmark
        print("\n[3] RUNNER BID INDEX EVALUATION (idx_bids_runner_status):")
        q_bid_idx = "SELECT Bid_ID FROM Bids WHERE Runner_ID = '25BCE0724' AND Bid_Status = 'pending'"
        q_bid_no_idx = "SELECT Bid_ID FROM Bids IGNORE INDEX (idx_bids_runner_status) WHERE Runner_ID = '25BCE0724' AND Bid_Status = 'pending'"

        bid_idx_avg, _ = benchmark_query(conn, q_bid_idx, "Bid Indexed")
        bid_no_idx_avg, _ = benchmark_query(conn, q_bid_no_idx, "Bid Unindexed")
        
        print(f"  * B-Tree Keyed Lookup (idx_bids_runner_status) : {bid_idx_avg:.4f} ms")
        print(f"  * Full Table Scan (IGNORE INDEX)               : {bid_no_idx_avg:.4f} ms")

    print("\n" + "=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_index_benchmark()