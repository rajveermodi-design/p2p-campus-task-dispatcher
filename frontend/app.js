// ============================================================================
// CAMPUS TASK DISPATCHER - APPLICATION CONTROLLER (ES6)
// Peer-to-Peer Errand Marketplace with Relational Escrow & ACID Telemetry
// ============================================================================

(function () {
    'use strict';

    // Application State
    const state = {
        currentUser: null,
        students: [],
        tasks: [],
        stats: null,
        activeFilter: 'all',
        searchQuery: '',
        selectedTaskId: null,
        pendingVerifyTaskId: null,
        radar: null,
        pollInterval: null
    };

    // DOM Element References
    const elements = {
        // Header & Profile
        currentUserName: document.getElementById('current-user-name'),
        currentUserAvatar: document.getElementById('current-user-avatar'),
        currentUserRegno: document.getElementById('current-user-regno'),
        currentUserRating: document.getElementById('current-user-rating'),
        currentWalletVal: document.getElementById('current-wallet-val'),
        btnOpenStudentSwitcher: document.getElementById('btn-open-student-switcher'),
        btnTopupWallet: document.getElementById('btn-topup-wallet'),
        btnToggleSound: document.getElementById('btn-toggle-sound'),
        soundIcon: document.getElementById('sound-icon'),
        btnResetDemo: document.getElementById('btn-reset-demo'),

        // Telemetry Strip
        metricTotalTasks: document.getElementById('metric-total-tasks'),
        metricOpenTasks: document.getElementById('metric-open-tasks'),
        metricEscrowHeld: document.getElementById('metric-escrow-held'),
        metricEscrowReleased: document.getElementById('metric-escrow-released'),
        metricCompletedTasks: document.getElementById('metric-completed-tasks'),
        metricTotalStudents: document.getElementById('metric-total-students'),
        metricAvgRating: document.getElementById('metric-avg-rating'),

        // Radar & Marketplace
        radarSvg: document.getElementById('campus-radar-svg'),
        radarActiveFlights: document.getElementById('radar-active-flights'),
        statusFilterTabs: document.getElementById('status-filter-tabs'),
        taskSearchInput: document.getElementById('task-search-input'),
        taskFeedContainer: document.getElementById('task-feed-container'),

        // Errand Post Form
        createTaskForm: document.getElementById('create-task-form'),
        taskPickupSelect: document.getElementById('task-pickup-select'),
        taskDropSelect: document.getElementById('task-drop-select'),
        taskBountyInput: document.getElementById('task-bounty-input'),
        taskPinInput: document.getElementById('task-pin-input'),
        btnGeneratePin: document.getElementById('btn-generate-pin'),

        // Inspector & Logs
        taskDetailInspector: document.getElementById('task-detail-inspector'),
        inspectorTaskTitle: document.getElementById('inspector-task-title'),
        inspectorContent: document.getElementById('inspector-content'),
        btnCloseInspector: document.getElementById('btn-close-inspector'),
        acidLogConsole: document.getElementById('acid-log-console'),
        btnClearLogs: document.getElementById('btn-clear-logs'),

        // Modals
        modalPinVerify: document.getElementById('modal-pin-verify'),
        btnClosePinModal: document.getElementById('btn-close-pin-modal'),
        btnCancelPinVerify: document.getElementById('btn-cancel-pin-verify'),
        btnConfirmPinVerify: document.getElementById('btn-confirm-pin-verify'),
        pinDigitBoxes: document.querySelectorAll('.pin-digit-box'),

        modalStudentSwitcher: document.getElementById('modal-student-switcher'),
        btnCloseStudentModal: document.getElementById('btn-close-student-modal'),
        studentsRosterList: document.getElementById('students-roster-list'),
        registerStudentForm: document.getElementById('register-student-form'),
        regStudentNo: document.getElementById('reg-student-no'),
        regStudentName: document.getElementById('reg-student-name'),
        regStudentEmail: document.getElementById('reg-student-email'),

        modalWalletDeposit: document.getElementById('modal-wallet-deposit'),
        btnCloseDepositModal: document.getElementById('btn-close-deposit-modal'),
        btnCancelDeposit: document.getElementById('btn-cancel-deposit'),
        toastContainer: document.getElementById('toast-container')
    };

    // ========================================================================
    // 1. INITIALIZATION
    // ========================================================================

    async function init() {
        // Initialize Radar visualization
        if (window.CampusRadar && elements.radarSvg) {
            state.radar = new window.CampusRadar(elements.radarSvg, {
                onTaskSelect: (taskId) => {
                    selectTaskForInspection(taskId);
                }
            });
        }

        setupEventListeners();
        setupPinInputs();

        // Initial Data Fetch
        await fetchStudents();
        await refreshAllData();

        // Polling every 4 seconds for live concurrency updates
        state.pollInterval = setInterval(async () => {
            await refreshAllData(true);
        }, 4000);

        logACID('acid', 'Air Traffic Dispatcher initialized with MySQL 8.0 InnoDB backend.');
    }

    // ========================================================================
    // 2. DATA FETCHING & SYNCHRONIZATION
    // ========================================================================

    async function fetchStudents() {
        try {
            const res = await fetch('/students');
            if (res.ok) {
                state.students = await res.json();
                if (!state.currentUser && state.students.length > 0) {
                    // Default to Rajveer Modi or first student
                    const defaultUser = state.students.find(s => s.reg_no === '25BCE0750') || state.students[0];
                    setCurrentUser(defaultUser);
                } else if (state.currentUser) {
                    // Update current user balance/rating in-place
                    const refreshed = state.students.find(s => s.reg_no === state.currentUser.reg_no);
                    if (refreshed) setCurrentUser(refreshed);
                }
                renderStudentsRoster();
            }
        } catch (err) {
            console.error('Error fetching students:', err);
        }
    }

    async function fetchTasks() {
        try {
            const res = await fetch('/tasks');
            if (res.ok) {
                state.tasks = await res.json();
                renderTaskFeed();
                if (state.radar) {
                    state.radar.setTasks(state.tasks);
                }
                const activeFlights = state.tasks.filter(t => t.status === 'open' || t.status === 'assigned');
                elements.radarActiveFlights.textContent = `${activeFlights.length} ACTIVE FLIGHTS`;
            }
        } catch (err) {
            console.error('Error fetching tasks:', err);
        }
    }

    async function fetchStats() {
        try {
            const res = await fetch('/system/stats');
            if (res.ok) {
                state.stats = await res.json();
                renderStats();
            }
        } catch (err) {
            console.error('Error fetching system stats:', err);
        }
    }

    async function refreshAllData(silent = false) {
        await Promise.all([fetchTasks(), fetchStats()]);
        // Also refresh current student balance
        if (state.currentUser) {
            try {
                const res = await fetch(`/students/${state.currentUser.reg_no}`);
                if (res.ok) {
                    const profile = await res.json();
                    state.currentUser.balance = parseFloat(profile.balance);
                    state.currentUser.trust_rating = parseFloat(profile.trust_rating);
                    elements.currentWalletVal.textContent = `₹${state.currentUser.balance.toFixed(2)}`;
                    elements.currentUserRating.textContent = `★ ${state.currentUser.trust_rating.toFixed(2)}`;
                }
            } catch (e) {}
        }
        // If an errand is currently inspected, refresh its bids too
        if (state.selectedTaskId) {
            renderTaskInspection(state.selectedTaskId, silent);
        }
    }

    // ========================================================================
    // 3. STUDENT IDENTITY MANAGEMENT
    // ========================================================================

    function setCurrentUser(student) {
        state.currentUser = student;
        elements.currentUserName.textContent = student.name;
        elements.currentUserRegno.textContent = student.reg_no;
        elements.currentUserRating.textContent = `★ ${parseFloat(student.trust_rating).toFixed(2)}`;
        elements.currentWalletVal.textContent = `₹${parseFloat(student.balance).toFixed(2)}`;

        // Initials avatar
        const initials = student.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        elements.currentUserAvatar.textContent = initials;

        logACID('acid', `Identity switched: [${student.reg_no}] ${student.name} (Wallet: ₹${student.balance})`);
        renderTaskFeed();
    }

    function renderStudentsRoster() {
        elements.studentsRosterList.innerHTML = '';
        state.students.forEach(student => {
            const isCurrent = state.currentUser && state.currentUser.reg_no === student.reg_no;
            const card = document.createElement('div');
            card.className = `profile-card ${isCurrent ? 'active-selected' : ''}`;
            card.style.justifyContent = 'space-between';
            card.style.background = isCurrent ? 'rgba(0, 229, 255, 0.12)' : 'var(--bg-surface)';
            card.style.borderColor = isCurrent ? 'var(--cyan-primary)' : 'var(--border-subtle)';

            const initials = student.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

            card.innerHTML = `
                <div style="display:flex;align-items:center;gap:12px;">
                    <div class="profile-avatar">${initials}</div>
                    <div class="profile-info">
                        <div class="profile-name">
                            ${student.name}
                            <span class="profile-rating">★ ${parseFloat(student.trust_rating).toFixed(2)}</span>
                            ${isCurrent ? '<span class="brand-badge" style="font-size:9px;">ACTIVE</span>' : ''}
                        </div>
                        <div class="profile-meta">${student.reg_no} • ${student.email}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:var(--font-mono);font-weight:700;color:var(--emerald-success);font-size:14px;">₹${parseFloat(student.balance).toFixed(2)}</div>
                    <button class="btn-secondary btn-select-student" style="padding:4px 8px;font-size:11px;margin-top:4px;">
                        ${isCurrent ? 'Selected' : 'Simulate'}
                    </button>
                </div>
            `;

            card.querySelector('.btn-select-student').addEventListener('click', (e) => {
                e.stopPropagation();
                if (window.soundFX) window.soundFX.click();
                setCurrentUser(student);
                closeModal(elements.modalStudentSwitcher);
                showToast(`Now simulating as ${student.name}`, 'info');
            });

            card.addEventListener('click', () => {
                if (window.soundFX) window.soundFX.click();
                setCurrentUser(student);
                closeModal(elements.modalStudentSwitcher);
                showToast(`Now simulating as ${student.name}`, 'info');
            });

            elements.studentsRosterList.appendChild(card);
        });
    }

    // ========================================================================
    // 4. TELEMETRY STATS RENDERING
    // ========================================================================

    function renderStats() {
        if (!state.stats) return;
        const { tasks, students, escrow } = state.stats;

        elements.metricTotalTasks.textContent = tasks.total;
        elements.metricOpenTasks.textContent = tasks.open;
        elements.metricEscrowHeld.textContent = `₹${escrow.held.toFixed(2)}`;
        elements.metricEscrowReleased.textContent = `₹${escrow.released.toFixed(2)}`;
        elements.metricCompletedTasks.textContent = tasks.completed;
        elements.metricTotalStudents.textContent = students.total;
        elements.metricAvgRating.textContent = students.avg_rating.toFixed(2);
    }

    // ========================================================================
    // 5. ERRAND MARKETPLACE FEED RENDERING
    // ========================================================================

    function renderTaskFeed() {
        let filtered = [...state.tasks];

        // Apply Status Filter Tab
        if (state.activeFilter === 'open') {
            filtered = filtered.filter(t => t.status === 'open');
        } else if (state.activeFilter === 'assigned') {
            filtered = filtered.filter(t => t.status === 'assigned');
        } else if (state.activeFilter === 'completed') {
            filtered = filtered.filter(t => t.status === 'completed');
        } else if (state.activeFilter === 'my-tasks') {
            if (state.currentUser) {
                filtered = filtered.filter(t => t.requester_id === state.currentUser.reg_no || t.runner_id === state.currentUser.reg_no);
            }
        }

        // Apply Search Query
        if (state.searchQuery.trim()) {
            const q = state.searchQuery.toLowerCase();
            filtered = filtered.filter(t => 
                t.pickup_location.toLowerCase().includes(q) ||
                t.drop_location.toLowerCase().includes(q) ||
                (t.requester_name && t.requester_name.toLowerCase().includes(q)) ||
                (t.runner_name && t.runner_name.toLowerCase().includes(q)) ||
                String(t.task_id).includes(q)
            );
        }

        elements.taskFeedContainer.innerHTML = '';

        if (filtered.length === 0) {
            elements.taskFeedContainer.innerHTML = `
                <div style="text-align:center;padding:48px 20px;color:var(--text-muted);background:var(--bg-glass-card);border-radius:var(--radius-lg);border:1px dashed var(--border-subtle);">
                    <div style="font-size:32px;margin-bottom:8px;">🛰️</div>
                    <div style="font-size:15px;color:#fff;font-weight:600;margin-bottom:4px;">No Errands Found</div>
                    <div style="font-size:12px;">No active flight paths match your filter criteria. Try posting a new errand!</div>
                </div>
            `;
            return;
        }

        filtered.forEach(task => {
            const card = document.createElement('div');
            card.className = `task-card status-${task.status} ${state.selectedTaskId === task.task_id ? 'active-selected' : ''}`;
            card.setAttribute('data-task-id', task.task_id);

            const isRequester = state.currentUser && state.currentUser.reg_no === task.requester_id;
            const isAssignedRunner = state.currentUser && state.currentUser.reg_no === task.runner_id;

            card.innerHTML = `
                <div class="task-header">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span class="task-id-badge">FLIGHT #${task.task_id}</span>
                        <span class="status-pill ${task.status}">
                            <span class="status-dot" style="background:currentColor;box-shadow:none;"></span>
                            ${task.status.toUpperCase()}
                        </span>
                        ${isRequester ? '<span class="brand-badge" style="background:rgba(139,92,246,0.15);color:var(--violet-accent);border-color:rgba(139,92,246,0.3);">MY ERRAND</span>' : ''}
                        ${isAssignedRunner ? '<span class="brand-badge" style="background:rgba(245,158,11,0.15);color:var(--amber-warning);border-color:rgba(245,158,11,0.3);">MY RUNNER TASK</span>' : ''}
                    </div>
                    <div class="bounty-display">
                        <div class="bounty-val">₹${parseFloat(task.bounty).toFixed(2)}</div>
                        <div class="escrow-subtext">Escrow: ${task.escrow_state || 'HELD'}</div>
                    </div>
                </div>

                <div class="waypoint-route">
                    <div class="waypoint">
                        <span class="waypoint-type">📍 Pickup Location</span>
                        <span class="waypoint-name">${task.pickup_location}</span>
                    </div>
                    <div class="waypoint-arrow">➔</div>
                    <div class="waypoint">
                        <span class="waypoint-type">🎯 Drop Location</span>
                        <span class="waypoint-name">${task.drop_location}</span>
                    </div>
                </div>

                <div class="task-footer">
                    <div class="stakeholder-info">
                        <div>
                            Requester: <strong style="color:#fff;">${task.requester_name || task.requester_id}</strong>
                            ${task.requester_rating ? `<span style="color:#fbbf24;">(★ ${parseFloat(task.requester_rating).toFixed(2)})</span>` : ''}
                        </div>
                        ${task.runner_id ? `
                            <div style="border-left:1px solid var(--border-subtle);padding-left:10px;">
                                Runner: <strong style="color:var(--amber-warning);">${task.runner_name || task.runner_id}</strong>
                            </div>
                        ` : ''}
                    </div>

                    ${isRequester && task.verification_pin ? `
                        <div style="font-family:var(--font-mono);font-size:11px;color:var(--violet-accent);background:rgba(139,92,246,0.1);padding:3px 8px;border-radius:4px;border:1px solid rgba(139,92,246,0.25);">
                            Secret PIN: <strong>${task.verification_pin}</strong>
                        </div>
                    ` : ''}
                </div>

                <!-- Action Button Row -->
                <div class="task-actions-row">
                    <div class="bids-chip-preview" id="bids-chip-${task.task_id}">
                        <span>👥 Click to view bids & inspection</span>
                    </div>

                    <div style="display:flex;gap:8px;">
                        ${task.status === 'open' && !isRequester ? `
                            <button class="btn-primary btn-bid-task" data-id="${task.task_id}" style="padding:6px 14px;font-size:12px;">
                                ⚡ Place Runner Bid
                            </button>
                        ` : ''}

                        ${task.status === 'open' && isRequester ? `
                            <button class="btn-secondary btn-inspect-task" data-id="${task.task_id}" style="padding:6px 12px;font-size:12px;">
                                📋 Review Bids
                            </button>
                            <button class="btn-danger btn-cancel-task" data-id="${task.task_id}" style="padding:6px 10px;font-size:11px;" title="Cancel & Refund Escrow">
                                Refund
                            </button>
                        ` : ''}

                        ${task.status === 'assigned' && isAssignedRunner ? `
                            <button class="btn-primary btn-verify-handover" data-id="${task.task_id}" style="padding:6px 14px;font-size:12px;background:linear-gradient(135deg,var(--emerald-success),#059669);">
                                🔐 Deliver & Enter PIN
                            </button>
                        ` : ''}

                        <button class="btn-secondary btn-inspect-task" data-id="${task.task_id}" style="padding:6px 10px;font-size:11.5px;">
                            Inspect
                        </button>
                    </div>
                </div>
            `;

            // Card click selects for inspection
            card.addEventListener('click', (e) => {
                // Ignore if clicked on an action button
                if (e.target.closest('button')) return;
                selectTaskForInspection(task.task_id);
            });

            // Button event listeners
            const btnBid = card.querySelector('.btn-bid-task');
            if (btnBid) {
                btnBid.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await handlePlaceBid(task.task_id);
                });
            }

            const btnInspectList = card.querySelectorAll('.btn-inspect-task');
            btnInspectList.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    selectTaskForInspection(task.task_id);
                });
            });

            const btnCancel = card.querySelector('.btn-cancel-task');
            if (btnCancel) {
                btnCancel.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await handleCancelTask(task.task_id);
                });
            }

            const btnVerify = card.querySelector('.btn-verify-handover');
            if (btnVerify) {
                btnVerify.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openPinVerifyModal(task.task_id);
                });
            }

            elements.taskFeedContainer.appendChild(card);
        });
    }

    // ========================================================================
    // 6. TASK INSPECTION & BID RESOLUTION (AIR TRAFFIC CONTROLLER)
    // ========================================================================

    async function selectTaskForInspection(taskId) {
        state.selectedTaskId = taskId;
        if (state.radar) state.radar.setActiveTask(taskId);
        if (window.soundFX) window.soundFX.ping();

        elements.taskDetailInspector.style.display = 'block';
        elements.inspectorTaskTitle.textContent = `ERRAND #${taskId} TELEMETRY & BIDS`;
        elements.taskDetailInspector.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        await renderTaskInspection(taskId);
        renderTaskFeed(); // Update highlight
    }

    async function renderTaskInspection(taskId, silent = false) {
        try {
            const [taskRes, bidsRes] = await Promise.all([
                fetch(`/tasks/${taskId}`),
                fetch(`/tasks/${taskId}/bids`)
            ]);

            if (!taskRes.ok) return;
            const task = await taskRes.json();
            const bids = bidsRes.ok ? await bidsRes.json() : [];

            const isRequester = state.currentUser && state.currentUser.reg_no === task.requester_id;
            const isAssigned = task.status === 'assigned';
            const isCompleted = task.status === 'completed';

            let bidsHtml = '';
            if (bids.length === 0) {
                bidsHtml = `<div style="color:var(--text-muted);font-size:12px;padding:12px 0;">No runner bids submitted yet.</div>`;
            } else {
                bidsHtml = `
                    <div style="display:flex;flex-direction:column;gap:8px;margin-top:10px;">
                        ${bids.map(bid => {
                            const isWinningBid = bid.bid_status === 'accepted';
                            const isRejected = bid.bid_status === 'rejected';
                            const badgeColor = isWinningBid ? 'var(--emerald-success)' : (isRejected ? 'var(--crimson-danger)' : 'var(--amber-warning)');

                            return `
                                <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.03);padding:8px 12px;border-radius:var(--radius-sm);border:1px solid rgba(255,255,255,0.05);">
                                    <div>
                                        <div style="font-weight:600;font-size:13px;color:#fff;">
                                            ${bid.runner_name} 
                                            <span style="font-family:var(--font-mono);font-size:11px;color:var(--text-secondary);">(${bid.runner_id})</span>
                                        </div>
                                        <div style="font-size:11px;color:var(--text-muted);">
                                            Rating: ★ ${bid.runner_rating.toFixed(2)} • Offered: ${new Date(bid.offered_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                        </div>
                                    </div>
                                    <div style="display:flex;align-items:center;gap:8px;">
                                        <span style="font-family:var(--font-mono);font-size:11px;color:${badgeColor};text-transform:uppercase;font-weight:700;">
                                            ${bid.bid_status}
                                        </span>
                                        ${task.status === 'open' && isRequester ? `
                                            <button class="btn-primary btn-assign-runner" data-task-id="${task.task_id}" data-runner-id="${bid.runner_id}" style="padding:4px 10px;font-size:11px;">
                                                ✓ Assign
                                            </button>
                                        ` : ''}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                `;
            }

            elements.inspectorContent.innerHTML = `
                <!-- Task Route & Escrow Meta -->
                <div style="background:rgba(0,0,0,0.3);padding:12px;border-radius:var(--radius-md);margin-bottom:14px;border:1px solid rgba(255,255,255,0.05);">
                    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-family:var(--font-mono);font-size:11px;color:var(--text-muted);">ESCROW LEDGER</span>
                        <span style="font-family:var(--font-mono);font-size:11px;color:var(--cyan-primary);font-weight:700;">TXN #${task.escrow ? task.escrow.txn_id : '---'}</span>
                    </div>
                    <div style="font-size:13px;display:flex;justify-content:space-between;align-items:center;">
                        <span>Held Amount: <strong>₹${parseFloat(task.bounty).toFixed(2)}</strong></span>
                        <span class="status-pill ${task.status}">${task.escrow ? task.escrow.state : 'HELD'}</span>
                    </div>
                    ${task.verification_pin && (isRequester || isCompleted) ? `
                        <div style="margin-top:8px;padding-top:8px;border-top:1px dashed rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:11.5px;color:var(--violet-accent);">Cryptographic Handover PIN:</span>
                            <span style="font-family:var(--font-mono);font-weight:700;font-size:14px;color:#fff;background:rgba(139,92,246,0.2);padding:2px 8px;border-radius:4px;">${task.verification_pin}</span>
                        </div>
                    ` : ''}
                </div>

                <!-- Bids Section -->
                <div>
                    <div style="font-family:var(--font-heading);font-weight:700;font-size:13px;color:#fff;display:flex;justify-content:space-between;">
                        <span>RUNNER BIDS (${bids.length})</span>
                        ${task.status === 'open' && isRequester ? '<span style="font-size:11px;color:var(--cyan-primary);">Click "Assign" to resolve</span>' : ''}
                    </div>
                    ${bidsHtml}
                </div>
            `;

            // Attach assign buttons
            const assignBtns = elements.inspectorContent.querySelectorAll('.btn-assign-runner');
            assignBtns.forEach(btn => {
                btn.addEventListener('click', async () => {
                    const tId = parseInt(btn.getAttribute('data-task-id'));
                    const rId = btn.getAttribute('data-runner-id');
                    await handleAssignRunner(tId, rId);
                });
            });

        } catch (err) {
            console.error('Error rendering inspection:', err);
        }
    }

    // ========================================================================
    // 7. ACTION HANDLERS (POST, BID, ASSIGN, COMPLETE, REFUND)
    // ========================================================================

    // Action 1: Create Task with Escrow
    async function handleCreateTask(e) {
        e.preventDefault();
        if (!state.currentUser) {
            showToast('Please select a student identity first', 'error');
            return;
        }

        const pickup = elements.taskPickupSelect.value;
        const drop = elements.taskDropSelect.value;
        const bounty = parseFloat(elements.taskBountyInput.value);
        const pin = elements.taskPinInput.value.trim();

        if (pickup === drop) {
            showToast('Pickup and drop destinations must be distinct campus locations', 'warn');
            return;
        }

        if (bounty > state.currentUser.balance) {
            if (window.soundFX) window.soundFX.error();
            showToast(`Insufficient Funds: Wallet balance is ₹${state.currentUser.balance.toFixed(2)}, need ₹${bounty.toFixed(2)}`, 'error');
            logACID('error', `[LOCK REJECT] User ${state.currentUser.reg_no} failed balance check on sp_post_task_with_escrow.`);
            return;
        }

        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', `[TRANSACTION START] CALL sp_post_task_with_escrow('${state.currentUser.reg_no}', '${pickup}', '${drop}', ${bounty}, '${pin}')`);

            const res = await fetch('/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    requester_id: state.currentUser.reg_no,
                    pickup_location: pickup,
                    drop_location: drop,
                    bounty: bounty,
                    verification_pin: pin
                })
            });

            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.dispatch();
                showToast(`Errand posted! ₹${bounty.toFixed(2)} frozen in Escrow ledger.`, 'success');
                logACID('success', `[COMMIT] Errand posted & ₹${bounty} held in Escrow_Transactions. Row exclusive lock released.`);
                // Reset PIN field with new random PIN
                generateRandomPin();
                await refreshAllData();
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'Failed to post task', 'error');
                logACID('error', `[ROLLBACK] ${data.detail || 'Execution failed'}`);
            }
        } catch (err) {
            console.error('Error posting task:', err);
            showToast('Network error while posting errand', 'error');
        }
    }

    // Action 2: Place Bid as Runner
    async function handlePlaceBid(taskId) {
        if (!state.currentUser) {
            showToast('Please select a student identity first', 'error');
            return;
        }

        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', `[INSERT Bids] Runner ${state.currentUser.reg_no} placing bid on Task #${taskId}`);

            const res = await fetch(`/tasks/${taskId}/bids`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_id: taskId,
                    runner_id: state.currentUser.reg_no
                })
            });

            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.ping();
                showToast(`Bid submitted for Errand #${taskId}!`, 'success');
                logACID('success', `[COMMIT] Bid registered in Bids table for Task #${taskId}.`);
                await refreshAllData();
                selectTaskForInspection(taskId);
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'Failed to place bid', 'error');
                logACID('error', `[SIGNAL 45000 / CONSTRAINT] ${data.detail}`);
            }
        } catch (err) {
            console.error('Error placing bid:', err);
            showToast('Network error submitting bid', 'error');
        }
    }

    // Action 3: Assign Runner to Task (Triggers trg_after_task_assignment)
    async function handleAssignRunner(taskId, runnerId) {
        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', `[UPDATE Tasks] Assigning Runner ${runnerId} to Task #${taskId} (X-Lock acquired)`);

            const res = await fetch(`/tasks/${taskId}/assign?runner_id=${encodeURIComponent(runnerId)}`, {
                method: 'POST'
            });

            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.dispatch();
                showToast(`Runner ${runnerId} assigned! Competing bids resolved automatically.`, 'success');
                logACID('success', `[TRIGGER FIRED] trg_after_task_assignment: Accepted ${runnerId}, marked competing bids rejected.`);
                await refreshAllData();
                selectTaskForInspection(taskId);
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'Assignment rejected', 'error');
                logACID('error', `[ASSIGNMENT ERROR] ${data.detail}`);
            }
        } catch (err) {
            console.error('Error assigning runner:', err);
            showToast('Network error during runner assignment', 'error');
        }
    }

    // Action 4: Cancel & Refund Task via sp_refund_abandoned_task
    async function handleCancelTask(taskId) {
        if (!confirm(`Are you sure you want to cancel Errand #${taskId} and refund escrow balance?`)) return;

        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', `[CALL sp_refund_abandoned_task] Refunding Escrow for Task #${taskId}`);

            const res = await fetch(`/tasks/${taskId}/cancel`, { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                if (window.soundFX) window.soundFX.ping();
                showToast(`Task #${taskId} cancelled and escrow funds refunded!`, 'info');
                logACID('success', `[COMMIT] Escrow_State -> REFUNDED. Balance restored to requester.`);
                await refreshAllData();
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'Refund failed', 'error');
                logACID('error', `[REFUND ERROR] ${data.detail}`);
            }
        } catch (err) {
            console.error('Error refunding task:', err);
            showToast('Network error during refund', 'error');
        }
    }

    // Action 5: Submit PIN & Complete Handover via sp_complete_task_handover
    async function handleConfirmPinVerification() {
        if (!state.pendingVerifyTaskId) return;

        const pinDigits = Array.from(elements.pinDigitBoxes).map(b => b.value).join('');
        if (pinDigits.length !== 4) {
            showToast('Please enter the full 4-digit verification PIN', 'warn');
            return;
        }

        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', `[CALL sp_complete_task_handover] Task #${state.pendingVerifyTaskId}, Runner: ${state.currentUser.reg_no}, PIN: ${pinDigits}`);

            const res = await fetch(`/tasks/${state.pendingVerifyTaskId}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    runner_id: state.currentUser.reg_no,
                    verification_pin: pinDigits
                })
            });

            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.success();
                closeModal(elements.modalPinVerify);
                showToast('Verification confirmed! Escrow funds released to your wallet!', 'success');
                logACID('success', `[ESCROW RELEASED] Escrow_State -> RELEASED. Bounty credited to runner wallet balance.`);
                await refreshAllData();
                selectTaskForInspection(state.pendingVerifyTaskId);
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'PIN verification failed', 'error');
                logACID('error', `[PIN AUTH FAILED] ${data.detail}`);
                // Shake PIN inputs
                elements.pinDigitBoxes.forEach(box => {
                    box.style.borderColor = 'var(--crimson-danger)';
                    setTimeout(() => box.style.borderColor = 'var(--border-subtle)', 800);
                });
            }
        } catch (err) {
            console.error('Error verifying PIN:', err);
            showToast('Network error during verification', 'error');
        }
    }

    // Action 6: Deposit Simulated Funds
    async function handleDepositFunds(amount) {
        if (!state.currentUser) return;
        try {
            const res = await fetch(`/students/${state.currentUser.reg_no}/deposit?amount=${amount}`, {
                method: 'POST'
            });
            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.ping();
                showToast(`Deposited ₹${amount}. New Balance: ₹${data.new_balance.toFixed(2)}`, 'success');
                logACID('acid', `[WALLET CREDIT] Credited ₹${amount} to ${state.currentUser.reg_no}.`);
                closeModal(elements.modalWalletDeposit);
                await fetchStudents();
            } else {
                showToast(data.detail || 'Deposit failed', 'error');
            }
        } catch (e) {
            showToast('Deposit failed', 'error');
        }
    }

    // Action 7: Register New Student
    async function handleRegisterStudent(e) {
        e.preventDefault();
        const regNo = elements.regStudentNo.value.trim().toUpperCase();
        const name = elements.regStudentName.value.trim();
        const email = elements.regStudentEmail.value.trim().toLowerCase();

        try {
            logACID('acid', `[INSERT Students] Registering student ${regNo} (${name})`);
            const res = await fetch('/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reg_no: regNo, name: name, email: email })
            });

            const data = await res.json();
            if (res.ok) {
                if (window.soundFX) window.soundFX.success();
                showToast(`Student ${name} registered successfully!`, 'success');
                elements.registerStudentForm.reset();
                await fetchStudents();
                // Switch to this new student
                const newStudent = state.students.find(s => s.reg_no === regNo);
                if (newStudent) setCurrentUser(newStudent);
                closeModal(elements.modalStudentSwitcher);
            } else {
                if (window.soundFX) window.soundFX.error();
                showToast(data.detail || 'Registration failed', 'error');
                logACID('error', `[REGISTRATION REJECTED] ${data.detail}`);
            }
        } catch (err) {
            showToast('Network error registering student', 'error');
        }
    }

    // Action 8: Reset Demo Data
    async function handleResetDemo() {
        if (!confirm('Reset all errands, bids, and student balances to baseline seed state?')) return;

        try {
            if (window.soundFX) window.soundFX.click();
            logACID('acid', '[SYSTEM RESET] Purging transactional tables and re-executing 05_seed_data.sql...');

            const res = await fetch('/system/reset', { method: 'POST' });
            const data = await res.json();

            if (res.ok) {
                if (window.soundFX) window.soundFX.dispatch();
                showToast('Database reset to clean baseline demo state!', 'success');
                logACID('success', '[RESET COMPLETE] Baseline tasks (Task 1: Open, Task 2: Assigned, Task 3: Completed) restored.');
                state.selectedTaskId = null;
                elements.taskDetailInspector.style.display = 'none';
                await fetchStudents();
                await refreshAllData();
            } else {
                showToast(data.detail || 'Reset failed', 'error');
            }
        } catch (err) {
            console.error('Error resetting database:', err);
            showToast('Network error during reset', 'error');
        }
    }

    // ========================================================================
    // 8. HELPERS, EVENT LISTENERS & MODALS
    // ========================================================================

    function generateRandomPin() {
        const rand = Math.floor(1000 + Math.random() * 9000).toString();
        elements.taskPinInput.value = rand;
        return rand;
    }

    function setupPinInputs() {
        elements.pinDigitBoxes.forEach((box, idx) => {
            box.addEventListener('input', (e) => {
                const val = e.target.value.replace(/[^0-9]/g, '');
                box.value = val;
                if (val && idx < elements.pinDigitBoxes.length - 1) {
                    elements.pinDigitBoxes[idx + 1].focus();
                }
            });

            box.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !box.value && idx > 0) {
                    elements.pinDigitBoxes[idx - 1].focus();
                } else if (e.key === 'Enter') {
                    handleConfirmPinVerification();
                }
            });
        });
    }

    function openPinVerifyModal(taskId) {
        state.pendingVerifyTaskId = taskId;
        elements.pinDigitBoxes.forEach(b => b.value = '');
        openModal(elements.modalPinVerify);
        setTimeout(() => elements.pinDigitBoxes[0].focus(), 100);
    }

    function openModal(modalEl) {
        if (!modalEl) return;
        modalEl.classList.add('active');
        if (window.soundFX) window.soundFX.ping();
    }

    function closeModal(modalEl) {
        if (!modalEl) return;
        modalEl.classList.remove('active');
    }

    function logACID(type, msg) {
        if (!elements.acidLogConsole) return;
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        entry.textContent = `[${time}] ${msg}`;
        elements.acidLogConsole.appendChild(entry);
        elements.acidLogConsole.scrollTop = elements.acidLogConsole.scrollHeight;
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icons = { success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️' };
        toast.innerHTML = `
            <span>${icons[type] || 'ℹ️'}</span>
            <span style="flex:1;">${message}</span>
        `;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = '0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    function setupEventListeners() {
        // Form submissions
        elements.createTaskForm.addEventListener('submit', handleCreateTask);
        elements.registerStudentForm.addEventListener('submit', handleRegisterStudent);

        // Random PIN button
        elements.btnGeneratePin.addEventListener('click', () => {
            if (window.soundFX) window.soundFX.click();
            generateRandomPin();
        });

        // Filter tabs
        const filterBtns = elements.statusFilterTabs.querySelectorAll('.tab-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (window.soundFX) window.soundFX.click();
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                state.activeFilter = btn.getAttribute('data-filter');
                renderTaskFeed();
            });
        });

        // Search input
        elements.taskSearchInput.addEventListener('input', (e) => {
            state.searchQuery = e.target.value;
            renderTaskFeed();
        });

        // Inspector close
        elements.btnCloseInspector.addEventListener('click', () => {
            elements.taskDetailInspector.style.display = 'none';
            state.selectedTaskId = null;
            if (state.radar) state.radar.setActiveTask(null);
            renderTaskFeed();
        });

        // Clear logs
        elements.btnClearLogs.addEventListener('click', () => {
            elements.acidLogConsole.innerHTML = '';
        });

        // Modals open / close triggers
        elements.btnOpenStudentSwitcher.addEventListener('click', () => {
            openModal(elements.modalStudentSwitcher);
        });
        elements.btnCloseStudentModal.addEventListener('click', () => {
            closeModal(elements.modalStudentSwitcher);
        });

        elements.btnTopupWallet.addEventListener('click', () => {
            openModal(elements.modalWalletDeposit);
        });
        elements.btnCloseDepositModal.addEventListener('click', () => {
            closeModal(elements.modalWalletDeposit);
        });
        elements.btnCancelDeposit.addEventListener('click', () => {
            closeModal(elements.modalWalletDeposit);
        });

        // Quick top-up amount buttons
        const topupBtns = document.querySelectorAll('.btn-quick-topup');
        topupBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const amount = parseFloat(btn.getAttribute('data-amount'));
                handleDepositFunds(amount);
            });
        });

        // PIN verify modal triggers
        elements.btnClosePinModal.addEventListener('click', () => {
            closeModal(elements.modalPinVerify);
        });
        elements.btnCancelPinVerify.addEventListener('click', () => {
            closeModal(elements.modalPinVerify);
        });
        elements.btnConfirmPinVerify.addEventListener('click', handleConfirmPinVerification);

        // Sound toggle
        elements.btnToggleSound.addEventListener('click', () => {
            if (window.soundFX) {
                const enabled = window.soundFX.toggle();
                elements.soundIcon.textContent = enabled ? '🔊' : '🔇';
                showToast(`Tactical Sound ${enabled ? 'Enabled' : 'Muted'}`, 'info');
            }
        });

        // Demo Reset
        elements.btnResetDemo.addEventListener('click', handleResetDemo);

        // Close modals on overlay backdrop click
        [elements.modalPinVerify, elements.modalStudentSwitcher, elements.modalWalletDeposit].forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) closeModal(overlay);
            });
        });
    }

    // Start on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
