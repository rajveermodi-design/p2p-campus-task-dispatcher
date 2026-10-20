import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "paper", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Academic styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 12,
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Colors
    c_client = "#EBF3FB"
    c_client_b = "#2B6CB0"
    c_app = "#EBFBF4"
    c_app_b = "#276749"
    c_db = "#FFF5F5"
    c_db_b = "#C53030"
    c_box_b = "#4A5568"

    # Title Banner
    ax.text(50, 97, "High-Concurrency P2P Campus Task Dispatcher: Architecture & Isolation Boundary", 
            ha='center', va='center', weight='bold', fontsize=11, color='#1A202C')

    # Tier 1: Client Tier
    rect_client = patches.FancyBboxPatch((2, 68), 24, 25, boxstyle="round,pad=1.2", 
                                         ec=c_client_b, fc=c_client, lw=1.5)
    ax.add_patch(rect_client)
    ax.text(14, 90, "Presentation Tier", ha='center', weight='bold', color=c_client_b, fontsize=10)
    ax.text(14, 83, "Student Requester (Web)\n* Task Creation & Escrow\n* PIN Verification Token", 
            ha='center', va='center', fontsize=8, color='#2D3748')
    ax.text(14, 73, "Student Runner (PWA)\n* Real-time Errand Feed\n* Atomic Bidding & Handover", 
            ha='center', va='center', fontsize=8, color='#2D3748')

    # Tier 2: Application Tier
    rect_app = patches.FancyBboxPatch((32, 68), 28, 25, boxstyle="round,pad=1.2", 
                                      ec=c_app_b, fc=c_app, lw=1.5)
    ax.add_patch(rect_app)
    ax.text(46, 90, "FastAPI ASGI Engine", ha='center', weight='bold', color=c_app_b, fontsize=10)
    ax.text(46, 83, "Pydantic V2 Contract Validation\n* Schema typing & JSON serialization\n* 4-Digit Token Verification Gateway", 
            ha='center', va='center', fontsize=8, color='#2D3748')
    ax.text(46, 73, "SQLAlchemy 2.0 Connection Pool\n* Pool Size = 10, Max Overflow = 20\n* pool_pre_ping = True, Liveness checks", 
            ha='center', va='center', fontsize=8, color='#2D3748')

    # Tier 3: Database Engine Tier
    rect_db = patches.FancyBboxPatch((66, 8), 32, 85, boxstyle="round,pad=1.5", 
                                     ec=c_db_b, fc=c_db, lw=1.8, ls='-')
    ax.add_patch(rect_db)
    ax.text(82, 90, "MySQL 8.0 InnoDB Engine", ha='center', weight='bold', color=c_db_b, fontsize=10)
    ax.text(82, 86, "Strict ACID & Repeatable Read", ha='center', style='italic', color='#742A2A', fontsize=8)

    # Subcomponents inside DB
    sb1 = patches.FancyBboxPatch((68, 66), 28, 17, boxstyle="round,pad=0.8", ec='#E53E3E', fc='#FFF5F5', lw=1.2)
    ax.add_patch(sb1)
    ax.text(82, 80, "Pessimistic Lock Boundary", ha='center', weight='bold', color='#9B2C2C', fontsize=8.5)
    ax.text(82, 73, "SELECT ... FOR UPDATE\nExclusive Row-Level X-Locks\nSerializes concurrent claims", 
            ha='center', va='center', fontsize=7.5, color='#2D3748')

    sb2 = patches.FancyBboxPatch((68, 44), 28, 19, boxstyle="round,pad=0.8", ec='#DD6B20', fc='#FFFAF0', lw=1.2)
    ax.add_patch(sb2)
    ax.text(82, 60, "ACID Stored Procedures", ha='center', weight='bold', color='#9C4221', fontsize=8.5)
    ax.text(82, 51, "sp_post_task_with_escrow\nsp_complete_task_handover\nsp_refund_abandoned_task", 
            ha='center', va='center', fontsize=7.5, family='monospace', color='#2D3748')

    sb3 = patches.FancyBboxPatch((68, 25), 28, 16, boxstyle="round,pad=0.8", ec='#319795', fc='#E6FFFA', lw=1.2)
    ax.add_patch(sb3)
    ax.text(82, 38, "Active Database Triggers", ha='center', weight='bold', color='#234E52', fontsize=8.5)
    ax.text(82, 31, "trg_prevent_self_bid (BEFORE)\ntrg_after_task_assignment (AFTER)\nAtomic bid adjudication", 
            ha='center', va='center', fontsize=7.5, family='monospace', color='#2D3748')

    sb4 = patches.FancyBboxPatch((68, 11), 28, 11, boxstyle="round,pad=0.8", ec='#4A5568', fc='#EDF2F7', lw=1.2)
    ax.add_patch(sb4)
    ax.text(82, 19, "Composite B-Tree Indexes", ha='center', weight='bold', color='#2D3748', fontsize=8.5)
    ax.text(82, 14, "idx_tasks_status_id | idx_bids_runner_status", 
            ha='center', va='center', fontsize=7.2, family='monospace', color='#2D3748')

    # Connectors
    ax.annotate("", xy=(32, 80), xytext=(26, 80),
                arrowprops=dict(arrowstyle="<->", color="#4A5568", lw=1.8))
    ax.text(29, 82, "REST", ha='center', fontsize=7.5, weight='bold', color="#4A5568")

    ax.annotate("", xy=(66, 80), xytext=(60, 80),
                arrowprops=dict(arrowstyle="<->", color="#4A5568", lw=1.8))
    ax.text(63, 82, "PyMySQL", ha='center', fontsize=7.5, weight='bold', color="#4A5568")

    # Lower context: Formal Guarantees
    rect_guar = patches.FancyBboxPatch((2, 8), 58, 52, boxstyle="round,pad=1.2", 
                                       ec=c_box_b, fc='#F7FAFC', lw=1.2)
    ax.add_patch(rect_guar)
    ax.text(31, 56, "Mathematical & Relational Integrity Guarantees", ha='center', weight='bold', color='#2D3748', fontsize=9.5)
    ax.text(31, 46, "[1] Boyce-Codd Normal Form (BCNF): Universal decomposition into Students,\n    Tasks, Bids, Escrow. Strictly eliminates update/delete anomalies.",
            ha='center', va='center', fontsize=8, color='#4A5568')
    ax.text(31, 34, "[2] Heath's Theorem Preservation: Lossless join reconstruction guarantees\n    R1 JOIN R2 JOIN R3 JOIN R4 = Universal Schema with zero spurious tuples.",
            ha='center', va='center', fontsize=8, color='#4A5568')
    ax.text(31, 22, "[3] Absolute Balance Invariant: Sum(Balance) + Sum(Escrow) = Initial Capital.\n    Zero double-spending under concurrent multi-threaded execution.",
            ha='center', va='center', fontsize=8, color='#4A5568')
    ax.text(31, 12, "[4] Zero Consensus Overhead: Sub-15ms transactional finality without\n    blockchain gas costs, mining delays, or PoW/PoS confirmation latency.",
            ha='center', va='center', fontsize=8, color='#2B6CB0', weight='bold')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig1_system_architecture.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig1_system_architecture.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig1_system_architecture")


def generate_escrow_fsm():
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # States
    states = [
        ("POSTED", 12, 55, "#E2E8F0", "#4A5568"),
        ("ESCROW_HELD", 40, 55, "#FEFCBF", "#B7791F"),
        ("IN_TRANSIT", 68, 55, "#BEE3F8", "#2B6CB0"),
        ("RELEASED\n(Terminal)", 92, 75, "#C6F6D5", "#22543D"),
        ("REFUNDED\n(Terminal)", 92, 25, "#FED7D7", "#9B2C2C")
    ]

    for name, x, y, fc, ec in states:
        box = patches.FancyBboxPatch((x-8, y-10), 16, 20, boxstyle="round,pad=0.8", ec=ec, fc=fc, lw=1.8)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', weight='bold', color=ec, fontsize=8)

    # Transitions
    ax.annotate("", xy=(32, 55), xytext=(20, 55),
                arrowprops=dict(arrowstyle="->", color="#2D3748", lw=1.5))
    ax.text(26, 62, "sp_post_task_with_escrow\n(Lock Requester Balance)", ha='center', fontsize=7, color="#2D3748")

    ax.annotate("", xy=(60, 55), xytext=(48, 55),
                arrowprops=dict(arrowstyle="->", color="#2D3748", lw=1.5))
    ax.text(54, 62, "Assign Runner\n(trg_after_task_assignment)", ha='center', fontsize=7, color="#2D3748")

    ax.annotate("", xy=(84, 75), xytext=(76, 62),
                arrowprops=dict(arrowstyle="->", color="#22543D", lw=1.8))
    ax.text(78, 80, "sp_complete_task_handover\n(Valid PIN + X-Lock on Task)", ha='center', fontsize=7, color="#22543D", weight='bold')

    ax.annotate("", xy=(84, 25), xytext=(74, 47),
                arrowprops=dict(arrowstyle="->", color="#9B2C2C", lw=1.8))
    ax.annotate("", xy=(84, 23), xytext=(48, 47),
                arrowprops=dict(arrowstyle="->", color="#9B2C2C", lw=1.4, linestyle="--"))
    ax.text(62, 30, "sp_refund_abandoned_task\n(Cancellation or Timeout)", ha='center', fontsize=7, color="#9B2C2C", weight='bold')

    box_inv = patches.FancyBboxPatch((10, 8), 80, 12, boxstyle="round,pad=0.5", ec='#3182CE', fc='#EBF8FF', lw=1.2)
    ax.add_patch(box_inv)
    ax.text(50, 14, "Financial Balance Invariant: Balance(Requester) + Balance(Runner) + Escrow(Task) = C_initial (Fixed)\nState transitions are atomic; partial updates cause immediate InnoDB transaction rollback.",
            ha='center', va='center', fontsize=7.5, color='#2B6CB0', weight='bold')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_escrow_fsm.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_escrow_fsm.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig2_escrow_fsm")


def generate_concurrency_race_timeline():
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    ax.text(20, 93, "Thread Alpha (Winner)", ha='center', weight='bold', color='#2B6CB0', fontsize=9.5)
    ax.plot([20, 20], [88, 12], color='#CBD5E0', lw=2, linestyle='--')

    ax.text(50, 93, "MySQL InnoDB Lock Manager", ha='center', weight='bold', color='#C53030', fontsize=9.5)
    ax.plot([50, 50], [88, 12], color='#CBD5E0', lw=2, linestyle='--')

    ax.text(80, 93, "Thread Beta (Competitor)", ha='center', weight='bold', color='#DD6B20', fontsize=9.5)
    ax.plot([80, 80], [88, 12], color='#CBD5E0', lw=2, linestyle='--')

    ax.text(5, 84, "t = 0 ms", fontsize=8, color='#718096')
    ax.annotate("POST /tasks/1/complete (PIN=4821)", xy=(48, 82), xytext=(22, 82),
                arrowprops=dict(arrowstyle="->", color="#2B6CB0", lw=1.2), fontsize=7.5)
    ax.annotate("POST /tasks/1/complete (PIN=4821)", xy=(52, 80), xytext=(78, 80),
                arrowprops=dict(arrowstyle="->", color="#DD6B20", lw=1.2), fontsize=7.5)

    ax.text(5, 70, "t = 1.2 ms", fontsize=8, color='#718096')
    ax.annotate("Acquires X-Lock on Task #1", xy=(22, 70), xytext=(48, 70),
                arrowprops=dict(arrowstyle="->", color="#276749", lw=1.4), fontsize=7.5, weight='bold')

    ax.annotate("BLOCKED on X-Lock Queue\n(InnoDB Lock Wait)", xy=(78, 62), xytext=(52, 62),
                arrowprops=dict(arrowstyle="->", color="#E53E3E", lw=1.4), fontsize=7.5, weight='bold')
    ax.fill_between([78, 82], [65, 65], [35, 35], color='#FED7D7', alpha=0.8)
    ax.text(80, 50, "Waiting on\nLock...", ha='center', va='center', fontsize=7, color='#9B2C2C')

    ax.text(5, 52, "t = 8.5 ms", fontsize=8, color='#718096')
    box_alpha = patches.FancyBboxPatch((12, 42), 16, 18, boxstyle="round,pad=0.5", ec='#2B6CB0', fc='#EBF8FF', lw=1.0)
    ax.add_patch(box_alpha)
    ax.text(20, 51, "1. Verify PIN = 4821\n2. Status -> 'completed'\n3. Escrow -> 'RELEASED'\n4. Balance -> Balance + 60", 
            ha='center', va='center', fontsize=6.8, color='#2C5282')

    ax.text(5, 36, "t = 14.97 ms", fontsize=8, color='#718096')
    ax.annotate("COMMIT & Release X-Lock", xy=(48, 36), xytext=(22, 36),
                arrowprops=dict(arrowstyle="->", color="#276749", lw=1.4), fontsize=7.5)
    ax.annotate("200 OK (Escrow Released)", xy=(10, 30), xytext=(20, 30),
                arrowprops=dict(arrowstyle="<-", color="#276749", lw=1.4), fontsize=7.5, weight='bold')

    ax.text(5, 24, "t = 15.02 ms", fontsize=8, color='#718096')
    ax.annotate("Lock Granted -> Reads Status", xy=(78, 24), xytext=(52, 24),
                arrowprops=dict(arrowstyle="->", color="#DD6B20", lw=1.2), fontsize=7.5)

    ax.text(5, 14, "t = 15.09 ms", fontsize=8, color='#718096')
    ax.annotate("Status != 'assigned' -> SIGNAL 45000", xy=(52, 14), xytext=(78, 14),
                arrowprops=dict(arrowstyle="->", color="#E53E3E", lw=1.4), fontsize=7.5)
    ax.annotate("400 Bad Request (Task Not Active)", xy=(90, 8), xytext=(80, 8),
                arrowprops=dict(arrowstyle="<-", color="#E53E3E", lw=1.4), fontsize=7.5, weight='bold')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_concurrency_race.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_concurrency_race.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig3_concurrency_race")


def generate_benchmark_latency_and_scaling():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2), dpi=300)

    categories = ['Marketplace Feed\n(Status Query)', 'Runner Bids\n(Runner_ID & Status)']
    x = np.arange(len(categories))
    width = 0.35

    unindexed_lat = [6.8837, 4.7457]
    indexed_lat = [4.6063, 0.4226]

    rects1 = ax1.bar(x - width/2, unindexed_lat, width, label='Full Table Scan', color='#CBD5E0', edgecolor='#4A5568')
    rects2 = ax1.bar(x + width/2, indexed_lat, width, label='Composite B-Tree Index', color='#3182CE', edgecolor='#1A365D')

    ax1.set_ylabel('Mean Query Latency (ms)')
    ax1.set_title('(a) Query Latency Optimization ($N=500$)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend(loc='upper right')
    ax1.grid(axis='y', linestyle=':', alpha=0.6)

    ax1.annotate('+33.1% speedup', xy=(x[0] + width/2, indexed_lat[0]), xytext=(x[0] + width/2 - 0.15, indexed_lat[0] + 0.8),
                 fontsize=8, weight='bold', color='#1A365D')
    ax1.annotate('11.2x speedup\n(91.1% gain)', xy=(x[1] + width/2, indexed_lat[1]), xytext=(x[1] + width/2 - 0.28, indexed_lat[1] + 1.2),
                 fontsize=8, weight='bold', color='#1A365D')

    threads = [1, 5, 10, 20, 30, 50]
    pessimistic_latency = [14.2, 18.5, 30.5, 48.2, 69.1, 98.4]
    naive_leakage = [0.0, 18.0, 36.4, 52.0, 68.5, 78.0]
    pessimistic_leakage = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    ax2.plot(threads, naive_leakage, marker='s', color='#E53E3E', lw=1.8, label='Naive App-Level (Leakage %)')
    ax2.plot(threads, pessimistic_leakage, marker='o', color='#38A169', lw=2.2, label='Proposed Lock (Leakage %)')

    ax2_twin = ax2.twinx()
    ax2_twin.plot(threads, pessimistic_latency, marker='^', color='#2B6CB0', lw=1.5, linestyle='--', label='Mean Latency (ms)')

    ax2.set_xlabel('Concurrent Contention Threads')
    ax2.set_ylabel('Escrow Leakage / Double-Spend Rate (%)', color='#E53E3E')
    ax2_twin.set_ylabel('Resolution Latency (ms)', color='#2B6CB0')
    ax2.set_title('(b) Contention Scaling & Invariant Preservation')
    ax2.set_ylim(-5, 100)
    ax2.grid(True, linestyle=':', alpha=0.6)

    lines_1, labels_1 = ax2.get_legend_handles_labels()
    lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center left', fontsize=7.8)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_latency_and_scaling.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_latency_and_scaling.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated fig4_latency_and_scaling")

if __name__ == "__main__":
    generate_system_architecture()
    generate_escrow_fsm()
    generate_concurrency_race_timeline()
    generate_benchmark_latency_and_scaling()
