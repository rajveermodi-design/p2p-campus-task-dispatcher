# IEEE Conference Manuscript

**Title:** A High-Concurrency Peer-to-Peer Campus Task Dispatcher with ACID-Compliant Escrow Isolation and Pessimistic Locking  
**Format:** IEEE Conference 2-Column Template (`IEEEtran.cls`)  
**Target Conferences:** IEEE TENCON, IEEE INDICON, IEEE COMPSAC, IEEE Cloud / CCNet, IEEE Access  

---

## Directory Contents

- **`manuscript.tex`**: The primary LaTeX source file containing the complete, revised research paper with formal proofs, algorithmic matching models, multi-worker concurrency evaluations, and 24 academic citations.
- **`figures/`**: Publication-grade vector PDF and 300-DPI raster PNG figures:
  - `fig1_system_architecture.{pdf,png}`: End-to-end 3-tier architecture with FastAPI ASGI, connection pooling, and MySQL InnoDB row-level locking boundaries.
  - `fig2_escrow_fsm.{pdf,png}`: Finite State Machine governing escrow states with atomic rollback boundaries.
  - `fig3_concurrency_race.{pdf,png}`: Execution timeline of InnoDB row-level lock serialization between competing payout threads.
  - `fig4_latency_and_scaling.{pdf,png}`: Dual-panel benchmark plots showing (a) query latency speedup and (b) multi-worker contention scaling & balance invariant preservation.

---

## How to Compile

### 1. In Overleaf (Recommended)
1. Zip the `paper/` folder (including `manuscript.tex` and the `figures/` folder).
2. Go to [Overleaf](https://www.overleaf.com), click **New Project** $\to$ **Upload Project**, and upload the zip file.
3. Overleaf will automatically compile with pdfLaTeX.

### 2. Locally via Command Line
The repository includes `IEEEtran.cls` and `tectonic` is pre-configured on this machine. To compile directly in one command:
```bash
cd paper
tectonic manuscript.tex
```
*(Or via standard TeX Live / MacTeX if installed):*
```bash
pdflatex manuscript.tex
pdflatex manuscript.tex
```

---

## Submission Checklist for Authors

- [ ] **Author Anonymization:** If your target conference enforces **Double-Blind Review**, comment out the `\author{...}` block and replace with `\author{Anonymous Author(s)}`.
- [ ] **Page Limit Verification:** Standard IEEE short papers are 4–6 pages; full papers are 6–8 pages. This manuscript is formatted to fit a standard 6-page IEEE conference submission.
- [ ] **Advisor / Co-Authors:** Remember to add your faculty advisor or project mentors to the author block prior to final camera-ready submission.
