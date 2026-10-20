import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "paper", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8.0,
    "axes.labelsize": 8.0,
    "axes.titlesize": 9.0,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.0,
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

def generate_system_architecture():
    # Double-column IEEE figure: 7.1 in x 3.4 in
    fig, ax = plt.subplots(figsize=(7.1, 3.4), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    c_client_bg, c_client_edge = "#F0F4F8", "#1E3A8A"
    c_app_bg, c_app_edge = "#ECFDF5", "#065F46"
    c_db_bg, c_db_edge = "#FEF2F2", "#991B1B"
    c_bot_bg, c_bot_edge = "#F8FAFC", "#334155"

    ax.text(50, 96.5, "High-Concurrency P2P Campus Task Dispatcher: Architecture & Isolation Boundary", 
            ha='center', va='center', weight='bold', fontsize=9.2, color='#0F172A')

    # Tier 1: Presentation Tier
    p1 = patches.FancyBboxPatch((2, 34), 24, 57, boxstyle="round,pad=0.8", ec=c_client_edge, fc=c_client_bg, lw=1.2)
    ax.add_patch(p1)
    ax.text(14, 87, "Presentation Tier", ha='center', weight='bold', color=c_client_edge, fontsize=8.5)
    ax.text(14, 82.5, "(Responsive Web / PWA)", ha='center', fontsize=6.8, style='italic', color='#475569')

    b_req = patches.FancyBboxPatch((3.5, 60), 21, 18, boxstyle="round,pad=0.4", ec='#94A3B8', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_req)
    ax.text(14, 73.5, "Student Requester", ha='center', weight='bold', fontsize=7.2, color='#1E293B')
    ax.text(14, 66.5, "Post Task \u2022 Fund Escrow\nOut-of-Band PIN Token", ha='center', fontsize=6.3, color='#475569')

    b_run = patches.FancyBboxPatch((3.5, 38), 21, 18, boxstyle="round,pad=0.4", ec='#94A3B8', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_run)
    ax.text(14, 51.5, "Student Runner", ha='center', weight='bold', fontsize=7.2, color='#1E293B')
    ax.text(14, 44.5, "Live Task Feed \u2022 Place Bid\nHandover Verification", ha='center', fontsize=6.3, color='#475569')

    # Tier 2: Application Tier
    p2 = patches.FancyBboxPatch((34, 34), 28, 57, boxstyle="round,pad=0.8", ec=c_app_edge, fc=c_app_bg, lw=1.2)
    ax.add_patch(p2)
    ax.text(48, 87, "FastAPI ASGI Engine", ha='center', weight='bold', color=c_app_edge, fontsize=8.5)
    ax.text(48, 82.5, "(Uvicorn \u2022 Python 3.14)", ha='center', fontsize=6.8, style='italic', color='#065F46')

    b_pyd = patches.FancyBboxPatch((35.5, 60), 25, 18, boxstyle="round,pad=0.4", ec='#A7F3D0', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_pyd)
    ax.text(48, 73.5, "Pydantic V2 Contract Layer", ha='center', weight='bold', fontsize=7.0, color='#065F46')
    ax.text(48, 66.5, "Schema Validation & Types\nToken Filtering & Rate Limit", ha='center', fontsize=6.3, color='#334155')

    b_sql = patches.FancyBboxPatch((35.5, 38), 25, 18, boxstyle="round,pad=0.4", ec='#A7F3D0', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_sql)
    ax.text(48, 51.5, "SQLAlchemy Connection Pool", ha='center', weight='bold', fontsize=7.0, color='#065F46')
    ax.text(48, 44.5, "Pool: 10 \u2022 Max Overflow: 20\npool_pre_ping Liveness", ha='center', fontsize=6.3, color='#334155')

    # Tier 3: Database Storage Tier
    p3 = patches.FancyBboxPatch((70, 34), 28, 57, boxstyle="round,pad=0.8", ec=c_db_edge, fc=c_db_bg, lw=1.2)
    ax.add_patch(p3)
    ax.text(84, 87, "MySQL 8.0 InnoDB Engine", ha='center', weight='bold', color=c_db_edge, fontsize=8.5)
    ax.text(84, 82.5, "(Strict ACID \u2022 Repeatable Read)", ha='center', fontsize=6.8, style='italic', color='#991B1B')

    b_lock = patches.FancyBboxPatch((71.5, 74), 25, 7.0, boxstyle="round,pad=0.3", ec='#F87171', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_lock)
    ax.text(84, 77.5, "Row Locks (FOR UPDATE)", ha='center', weight='bold', fontsize=6.4, color='#991B1B')

    b_sp = patches.FancyBboxPatch((71.5, 62.5), 25, 9.0, boxstyle="round,pad=0.3", ec='#FCA5A5', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_sp)
    ax.text(84, 68.2, "Transactional Stored Procedures", ha='center', weight='bold', fontsize=6.4, color='#991B1B')
    ax.text(84, 64.5, "sp_post \u2022 sp_complete \u2022 sp_refund", ha='center', fontsize=5.8, family='monospace', color='#334155')

    b_trg = patches.FancyBboxPatch((71.5, 51), 25, 9.0, boxstyle="round,pad=0.3", ec='#FCA5A5', fc='#FFFFFF', lw=0.7)
    ax.add_patch(b_trg)
    ax.text(84, 56.7, "Active Database Triggers", ha='center', weight='bold', fontsize=6.4, color='#991B1B')
    ax.text(84, 53.0, "trg_self_bid \u2022 trg_after_assign", ha='center', fontsize=5.8, family='monospace', color='#334155')

    b_idx = patches.FancyBboxPatch((71.5, 39.5), 25, 9.0, boxstyle="round,pad=0.3", ec='#CBD5E1', fc='#F1F5F9', lw=0.7)
    ax.add_patch(b_idx)
    ax.text(84, 45.2, "Composite B-Tree Indexes", ha='center', weight='bold', fontsize=6.4, color='#1E293B')
    ax.text(84, 41.5, "idx_tasks_status \u2022 idx_bids_runner", ha='center', fontsize=5.6, family='monospace', color='#475569')

    # Connectors
    ax.annotate("", xy=(33.5, 62), xytext=(26.5, 62), arrowprops=dict(arrowstyle="<->", color="#0F172A", lw=1.2))
    ax.text(30, 65, "REST\nJSON", ha='center', fontsize=6.4, weight='bold', color="#0F172A")

    ax.annotate("", xy=(69.5, 62), xytext=(62.5, 62), arrowprops=dict(arrowstyle="<->", color="#0F172A", lw=1.2))
    ax.text(66, 65, "PyMySQL\nTCP", ha='center', fontsize=6.4, weight='bold', color="#0F172A")

    # Bottom Banner: 4 Formal Invariants
    p4 = patches.FancyBboxPatch((2, 4), 96, 27, boxstyle="round,pad=0.8", ec=c_bot_edge, fc=c_bot_bg, lw=1.2)
    ax.add_patch(p4)
    ax.text(50, 27.5, "Core Formal, Mathematical, and Concurrency Guarantees", 
            ha='center', weight='bold', color='#1E293B', fontsize=8.0)

    pillars = [
        ("Boyce-Codd Normal Form", "Schema decomposed to BCNF;\nZero update/delete anomalies.", 3.5),
        ("Lossless Reconstruction", "Heath's Theorem guarantees:\nR1 JOIN R2 JOIN R3 JOIN R4 = U.", 27.5),
        ("Balance Invariant", "Sum(Bal) + Escrow = Const;\n0.0% leakage under contention.", 51.5),
        ("Sub-35ms Resolution", "Direct B-Tree index traversal;\nDeterministic zero-leak finality.", 75.5),
    ]

    for title, desc, px in pillars:
        box_pil = patches.FancyBboxPatch((px, 6.5), 21.5, 18, boxstyle="round,pad=0.3", ec='#CBD5E1', fc='#FFFFFF', lw=0.6)
        ax.add_patch(box_pil)
        ax.text(px + 10.75, 20.5, title, ha='center', weight='bold', fontsize=6.5, color='#0F172A')
        ax.text(px + 10.75, 12.8, desc, ha='center', va='center', fontsize=5.6, color='#475569')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig1_system_architecture.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig1_system_architecture.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Cleanly regenerated fig1_system_architecture")


def generate_escrow_fsm():
    # Exactly designed for single-column IEEE width: 3.5 in x 2.3 in
    fig, ax = plt.subplots(figsize=(3.5, 2.3), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    def draw_state(name, subtext, cx, cy, w, h, fc, ec, tc):
        box = patches.FancyBboxPatch((cx - w/2, cy - h/2), w, h, 
                                     boxstyle='round,pad=0,rounding_size=2.0', 
                                     ec=ec, fc=fc, lw=1.1)
        ax.add_patch(box)
        if subtext:
            ax.text(cx, cy + 2.0, name, ha='center', va='center', weight='bold', color=tc, fontsize=5.8)
            ax.text(cx, cy - 2.2, subtext, ha='center', va='center', fontsize=4.5, color=tc)
        else:
            ax.text(cx, cy, name, ha='center', va='center', weight='bold', color=tc, fontsize=5.4)

    y_top = 62
    y_bot = 24

    draw_state('POSTED', None, 9.5, y_top, 15.0, 11.0, '#F1F5F9', '#475569', '#334155')
    draw_state('HELD', None, 49.0, y_top, 13.0, 11.0, '#FEF3C7', '#D97706', '#92400E')
    draw_state('IN-TRANSIT', None, 90.5, y_top, 17.0, 11.0, '#E0F2FE', '#0284C7', '#0369A1')
    draw_state('REFUNDED', '(Terminal)', 49.0, y_bot, 17.0, 13.0, '#FEE2E2', '#DC2626', '#991B1B')
    draw_state('RELEASED', '(Terminal)', 90.5, y_bot, 17.0, 13.0, '#DCFCE7', '#16A34A', '#15803D')

    # Arrow 1: POSTED (x: 2.0 to 17.0) -> HELD (x: 42.5 to 55.5)
    ax.annotate('', xy=(41.5, y_top), xytext=(18.0, y_top), 
                arrowprops=dict(arrowstyle='->', color='#1E293B', lw=1.1))
    ax.text(29.8, y_top + 2.5, 'sp_post_task', ha='center', va='bottom', fontsize=5.4, weight='bold', color='#0F172A')

    # Arrow 2: HELD (ends at 55.5) -> IN-TRANSIT (starts at 82.0)
    ax.annotate('', xy=(81.0, y_top), xytext=(56.5, y_top), 
                arrowprops=dict(arrowstyle='->', color='#1E293B', lw=1.1))
    ax.text(68.5, y_top + 2.5, 'Assign Runner', ha='center', va='bottom', fontsize=5.3, weight='bold', color='#0F172A')

    # Arrow 3: IN-TRANSIT -> RELEASED (Vertical Down)
    ax.annotate('', xy=(90.5, y_bot + 6.5), xytext=(90.5, y_top - 5.5), 
                arrowprops=dict(arrowstyle='->', color='#16A34A', lw=1.2))
    ax.text(91.8, (y_top + y_bot)/2 + 1.8, 'sp_complete', ha='left', va='center', fontsize=5.2, color='#15803D', weight='bold')
    ax.text(91.8, (y_top + y_bot)/2 - 2.8, '(PIN Verified)', ha='left', va='center', fontsize=4.5, color='#15803D')

    # Arrow 4: HELD -> REFUNDED (Vertical Down)
    ax.annotate('', xy=(49.0, y_bot + 6.5), xytext=(49.0, y_top - 5.5), 
                arrowprops=dict(arrowstyle='->', color='#DC2626', lw=1.1))
    ax.text(47.5, (y_top + y_bot)/2 + 1.8, 'sp_refund', ha='right', va='center', fontsize=5.2, color='#B91C1C', weight='bold')
    ax.text(47.5, (y_top + y_bot)/2 - 2.8, '(Cancel / Timeout)', ha='right', va='center', fontsize=4.5, color='#B91C1C')

    # Arrow 5: IN-TRANSIT -> REFUNDED (Diagonal Dashed)
    ax.annotate('', xy=(58.0, y_bot + 6.5), xytext=(82.0, y_top - 5.5), 
            arrowprops=dict(arrowstyle='->', color='#DC2626', lw=0.9, linestyle='--'))
    ax.text(70.0, (y_top + y_bot)/2 - 0.5, 'Dispute / Abort', ha='center', va='center', fontsize=4.4, color='#DC2626', 
            style='italic', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='#FCA5A5', lw=0.5))

    # Bottom Invariant Note
    ax.text(50, 7.5, 'Invariant: Balance(Req) + Balance(Run) + Escrow = C_0', 
            ha='center', va='center', fontsize=5.2, color='#0369A1', weight='bold')
    ax.text(50, 3.0, '2PL Strict Serializability: Partial transitions roll back atomically.', 
            ha='center', va='center', fontsize=4.6, color='#475569')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_escrow_fsm.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig2_escrow_fsm.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Cleanly regenerated fig2_escrow_fsm")


def generate_concurrency_race_timeline():
    # Sequence diagram: 3.5 in x 3.3 in
    fig, ax = plt.subplots(figsize=(3.5, 3.3), dpi=300)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(-2, 102)

    xa, xdb, xb = 20, 50, 80

    ax.text(xa, 97.0, "Thread Alpha\n(Claimant 1)", ha='center', weight='bold', color='#1E40AF', fontsize=6.8)
    ax.text(xdb, 97.0, "MySQL InnoDB\nLock Manager", ha='center', weight='bold', color='#991B1B', fontsize=6.8)
    ax.text(xb, 97.0, "Thread Beta\n(Claimant 2)", ha='center', weight='bold', color='#C2410C', fontsize=6.8)

    ax.plot([xa, xa], [90, 8], color='#CBD5E1', lw=1.2, linestyle='--')
    ax.plot([xdb, xdb], [90, 8], color='#CBD5E1', lw=1.2, linestyle='--')
    ax.plot([xb, xb], [90, 8], color='#CBD5E1', lw=1.2, linestyle='--')

    # Step 1: Request (t=0ms)
    y1 = 84
    ax.text(2, y1, "0ms", fontsize=5.6, color='#64748B')
    ax.annotate("", xy=(xdb-2, y1), xytext=(xa+2, y1), arrowprops=dict(arrowstyle="->", color="#1E40AF", lw=1.0))
    ax.annotate("", xy=(xdb+2, y1), xytext=(xb-2, y1), arrowprops=dict(arrowstyle="->", color="#C2410C", lw=1.0))
    ax.text(35, y1+2.2, "Claim Payout", ha='center', fontsize=5.4, color="#1E40AF")
    ax.text(65, y1+2.2, "Claim Payout", ha='center', fontsize=5.4, color="#C2410C")

    # Step 2: X-Lock Granted (1.2ms)
    y2 = 74
    ax.text(2, y2, "1.2ms", fontsize=5.6, color='#64748B')
    ax.annotate("", xy=(xa+2, y2), xytext=(xdb-2, y2), arrowprops=dict(arrowstyle="->", color="#15803D", lw=1.1))
    ax.text(35, y2+2.2, "X-Lock Granted", ha='center', fontsize=5.4, color="#15803D", weight='bold')

    # Beta Blocked bar
    ax.fill_between([xb-4, xb+4], [76, 76], [41, 41], color='#FEE2E2', alpha=0.9, ec='#F87171', lw=0.6)
    ax.text(xb, 58.5, "BLOCKED\non X-Lock\nQueue", ha='center', va='center', fontsize=5.0, color='#991B1B', weight='bold')

    # Alpha Active Execution bar
    ax.fill_between([xa-4, xa+4], [74, 74], [39, 39], color='#DCFCE7', alpha=0.9, ec='#86EFAC', lw=0.6)

    # Step 3: Alpha Processing Note (placed between Alpha and DB, x: 24 to 46)
    y3 = 56.5
    ax.text(2, y3, "8.5ms", fontsize=5.6, color='#64748B')
    box_proc = patches.FancyBboxPatch((24, y3-11), 22, 21, boxstyle="round,pad=0.3", ec='#93C5FD', fc='#EFF6FF', lw=0.6)
    ax.add_patch(box_proc)
    ax.text(35, y3+7.5, "sp_complete", ha='center', weight='bold', fontsize=5.4, color='#1E40AF')
    ax.text(35, y3+4.0, "\u2022 PIN Match: Valid\n\u2022 Status: 'completed'\n\u2022 Escrow: 'RELEASED'\n\u2022 Credit Runner Wallet", 
            ha='center', va='top', fontsize=4.6, color='#1E293B')

    # Step 4: Alpha Commits (14.9ms)
    y4 = 39
    ax.text(2, y4, "14.9ms", fontsize=5.6, color='#64748B')
    ax.annotate("", xy=(xdb-2, y4), xytext=(xa+2, y4), arrowprops=dict(arrowstyle="->", color="#15803D", lw=1.1))
    ax.text(35, y4+2.2, "COMMIT & Unlock", ha='center', fontsize=5.4, color="#15803D", weight='bold')
    ax.text(xa, y4-6.5, "HTTP 200 OK\n(Payout Released)", ha='center', fontsize=5.2, color="#15803D", weight='bold')

    # Step 5: Beta Granted Lock (15.0ms)
    y5 = 26
    ax.text(2, y5, "15.0ms", fontsize=5.6, color='#64748B')
    ax.annotate("", xy=(xb-2, y5), xytext=(xdb+2, y5), arrowprops=dict(arrowstyle="->", color="#C2410C", lw=1.0))
    ax.text(65, y5+2.2, "Lock Granted -> Reads Status", ha='center', fontsize=5.0, color="#C2410C")

    # Step 6: Beta Rejection (15.1ms)
    y6 = 14
    ax.text(2, y6, "15.1ms", fontsize=5.6, color='#64748B')
    ax.text(xb, y6+2.5, "Status != 'assigned'", ha='center', fontsize=5.0, color="#DC2626")
    ax.text(xb, y6-2.5, "SIGNAL 45000: HTTP 400\n(Task Not Active)", ha='center', fontsize=5.0, color="#DC2626", weight='bold')

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_concurrency_race.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig3_concurrency_race.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Cleanly regenerated fig3_concurrency_race")


def generate_benchmark_latency_and_scaling():
    # Full-width figure (7.1 x 2.4 inches) with ample subplot separation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.1, 2.4), dpi=300)
    fig.subplots_adjust(wspace=0.35)

    categories = ['Marketplace Feed\n(Status Query)', 'Runner Bids Lookup\n(Runner_ID & Status)']
    x = np.arange(len(categories))
    width = 0.32

    unindexed_lat = [6.8837, 4.7457]
    indexed_lat = [4.6063, 0.4226]

    rects1 = ax1.bar(x - width/2, unindexed_lat, width, label='Full Table Scan', color='#CBD5E1', edgecolor='#475569', lw=0.8)
    rects2 = ax1.bar(x + width/2, indexed_lat, width, label='Composite B-Tree Index', color='#2563EB', edgecolor='#1E40AF', lw=0.8)

    ax1.set_ylabel('Mean Query Latency (ms)', fontsize=8.2)
    ax1.set_title('(a) Query Latency Optimization ($N=500$)', fontsize=8.8, weight='bold', pad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=7.8)
    ax1.legend(loc='upper right', frameon=True, fontsize=7.0)
    ax1.set_ylim(0, 8.5)
    ax1.grid(axis='y', linestyle=':', alpha=0.6)

    ax1.annotate('+33.1% speedup\n(495 rows scanned)', 
                 xy=(x[0] + width/2, indexed_lat[0]), 
                 xytext=(x[0] + width/2 - 0.12, 5.8),
                 fontsize=6.8, weight='bold', color='#1E40AF')

    ax1.annotate('11.2x speedup\n(91.1% gain \u2022 5 rows)', 
                 xy=(x[1] + width/2, indexed_lat[1]), 
                 xytext=(x[1] + width/2 - 0.28, 1.8),
                 fontsize=6.8, weight='bold', color='#1E40AF')

    threads = [1, 5, 10, 20, 30, 50]
    pessimistic_latency = [14.2, 18.5, 30.5, 48.2, 69.1, 98.4]
    naive_leakage = [0.0, 18.0, 30.0, 50.0, 68.5, 78.0]
    pessimistic_leakage = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    line1, = ax2.plot(threads, naive_leakage, marker='s', markersize=4, color='#DC2626', lw=1.6, label='Naive App-Level (Leakage %)')
    line2, = ax2.plot(threads, pessimistic_leakage, marker='o', markersize=4, color='#16A34A', lw=2.0, label='Pessimistic Lock (Leakage %)')

    ax2_twin = ax2.twinx()
    line3, = ax2_twin.plot(threads, pessimistic_latency, marker='^', markersize=4, color='#2563EB', lw=1.4, linestyle='--', label='Resolution Latency (ms)')

    ax2.set_xlabel('Concurrent Contention Threads', fontsize=8.2)
    ax2.set_ylabel('Escrow Leakage Rate (%)', color='#DC2626', fontsize=8.2)
    ax2_twin.set_ylabel('Mean Latency (ms)', color='#2563EB', fontsize=8.2)
    ax2.set_title('(b) Contention Scaling & Invariant Preservation', fontsize=8.8, weight='bold', pad=8)
    ax2.set_ylim(-5, 95)
    ax2_twin.set_ylim(0, 120)
    ax2.grid(True, linestyle=':', alpha=0.5)

    ax2.legend([line1, line2, line3], 
               ['Naive Leakage (%)', 'Pessimistic Leakage (0.0%)', 'Pessimistic Latency (ms)'], 
               loc='upper left', frameon=True, fontsize=6.8)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_latency_and_scaling.pdf"), bbox_inches='tight')
    fig.savefig(os.path.join(OUTPUT_DIR, "fig4_latency_and_scaling.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Cleanly regenerated fig4_latency_and_scaling")


if __name__ == "__main__":
    generate_system_architecture()
    generate_escrow_fsm()
    generate_concurrency_race_timeline()
    generate_benchmark_latency_and_scaling()
