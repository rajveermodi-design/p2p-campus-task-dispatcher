// ============================================================================
// CAMPUS AIR TRAFFIC RADAR & FLIGHT PATH VISUALIZATION
// Renders active errand flight paths across VIT campus nodes.
// ============================================================================

class CampusRadar {
    constructor(svgElement, options = {}) {
        this.svg = svgElement;
        this.options = options;
        this.landmarks = [
            { id: "food_mall", name: "Food Mall Ground Floor", short: "Food Mall", x: 260, y: 380, type: "dining", icon: "🍔" },
            { id: "tt", name: "Technology Tower (TT) 412", short: "Tech Tower (TT)", x: 620, y: 160, type: "academic", icon: "🏛️" },
            { id: "library", name: "Main Library Reprography", short: "Central Library", x: 420, y: 220, type: "library", icon: "📚" },
            { id: "sjt", name: "SJT Block 3rd Floor Lab", short: "SJT Block", x: 740, y: 360, type: "academic", icon: "💻" },
            { id: "hostel_d", name: "Men's Hostel Block D", short: "Men's Hostel (D)", x: 140, y: 180, type: "hostel", icon: "🏢" },
            { id: "hostel_l", name: "Men's Hostel Block L 204", short: "Men's Hostel (L)", x: 180, y: 300, type: "hostel", icon: "🛏️" },
            { id: "ladies_hostel", name: "Ladies Hostel Block A", short: "Ladies Hostel (A)", x: 500, y: 440, type: "hostel", icon: "🌸" },
            { id: "mb", name: "MB Ground Reprographics", short: "Main Building (MB)", x: 440, y: 90, type: "academic", icon: "🏫" },
            { id: "prp", name: "PRP Building Lounge", short: "PRP Block", x: 340, y: 480, type: "academic", icon: "🔬" }
        ];
        this.tasks = [];
        this.activeTaskId = null;
        this.onTaskSelect = options.onTaskSelect || (() => {});
    }

    // Match task pickup/drop string to closest known campus landmark
    findLandmark(locationString) {
        if (!locationString) return null;
        const lower = locationString.toLowerCase();
        
        if (lower.includes("food mall") || lower.includes("cafeteria")) {
            return this.landmarks.find(l => l.id === "food_mall");
        }
        if (lower.includes("technology tower") || lower.includes("tt")) {
            return this.landmarks.find(l => l.id === "tt");
        }
        if (lower.includes("library") || lower.includes("reprography")) {
            return this.landmarks.find(l => l.id === "library");
        }
        if (lower.includes("sjt")) {
            return this.landmarks.find(l => l.id === "sjt");
        }
        if (lower.includes("block d")) {
            return this.landmarks.find(l => l.id === "hostel_d");
        }
        if (lower.includes("block l")) {
            return this.landmarks.find(l => l.id === "hostel_l");
        }
        if (lower.includes("ladies") || lower.includes("lh")) {
            return this.landmarks.find(l => l.id === "ladies_hostel");
        }
        if (lower.includes("mb") || lower.includes("main building")) {
            return this.landmarks.find(l => l.id === "mb");
        }
        if (lower.includes("prp")) {
            return this.landmarks.find(l => l.id === "prp");
        }
        
        // Fallback default
        return this.landmarks[0];
    }

    setTasks(tasks) {
        this.tasks = tasks || [];
        this.render();
    }

    setActiveTask(taskId) {
        this.activeTaskId = taskId;
        this.render();
    }

    render() {
        if (!this.svg) return;
        const width = 880;
        const height = 560;

        // Colors
        const statusColors = {
            open: "#00e5ff",       // Cyan
            assigned: "#f59e0b",   // Amber
            in_transit: "#eab308", // Yellow
            completed: "#10b981",  // Emerald
            cancelled: "#64748b"   // Slate
        };

        let svgHtml = `
            <defs>
                <!-- Radar grid radial gradient -->
                <radialGradient id="radarBg" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#0e1b2f" stop-opacity="0.95" />
                    <stop offset="70%" stop-color="#0a1220" stop-opacity="0.98" />
                    <stop offset="100%" stop-color="#060a12" stop-opacity="1" />
                </radialGradient>

                <!-- Sweep gradient -->
                <linearGradient id="sweepGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.25" />
                    <stop offset="60%" stop-color="#00e5ff" stop-opacity="0.05" />
                    <stop offset="100%" stop-color="#00e5ff" stop-opacity="0" />
                </linearGradient>

                <!-- Glow filters -->
                <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="glowAmber" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="glowEmerald" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>

                <!-- Arrow markers -->
                <marker id="arrow-open" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#00e5ff" />
                </marker>
                <marker id="arrow-assigned" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b" />
                </marker>
                <marker id="arrow-completed" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
                </marker>
            </defs>

            <!-- Background -->
            <rect width="${width}" height="${height}" fill="url(#radarBg)" rx="16" />

            <!-- Radar Concentric Rings -->
            <g class="radar-grid" opacity="0.25" stroke="#00e5ff" fill="none">
                <circle cx="${width/2}" cy="${height/2}" r="80" stroke-width="1" stroke-dasharray="3 3" />
                <circle cx="${width/2}" cy="${height/2}" r="160" stroke-width="1" stroke-dasharray="4 4" />
                <circle cx="${width/2}" cy="${height/2}" r="240" stroke-width="1" stroke-dasharray="5 5" />
                <circle cx="${width/2}" cy="${height/2}" r="320" stroke-width="1" />
                <!-- Crosshairs -->
                <line x1="40" y1="${height/2}" x2="${width-40}" y2="${height/2}" stroke-width="1" stroke-dasharray="2 4" />
                <line x1="${width/2}" y1="30" x2="${width/2}" y2="${height-30}" stroke-width="1" stroke-dasharray="2 4" />
                <!-- 45-degree diagonals -->
                <line x1="${width/2 - 200}" y1="${height/2 - 200}" x2="${width/2 + 200}" y2="${height/2 + 200}" stroke-width="0.5" stroke-dasharray="1 5" />
                <line x1="${width/2 - 200}" y1="${height/2 + 200}" x2="${width/2 + 200}" y2="${height/2 - 200}" stroke-width="0.5" stroke-dasharray="1 5" />
            </g>

            <!-- Rotating Radar Sweep Line -->
            <g class="radar-sweep" style="transform-origin: ${width/2}px ${height/2}px;">
                <path d="M ${width/2} ${height/2} L ${width/2} ${height/2 - 320} A 320 320 0 0 1 ${width/2 + 180} ${height/2 - 264} Z" fill="url(#sweepGradient)" />
                <line x1="${width/2}" y1="${height/2}" x2="${width/2}" y2="${height/2 - 320}" stroke="#00e5ff" stroke-width="1.5" opacity="0.8" />
            </g>

            <!-- Campus Perimeter Watermarks -->
            <g opacity="0.3" fill="#64748b" font-family="'JetBrains Mono', monospace" font-size="10">
                <text x="24" y="32">SECTOR: VELLORE CAMPUS (VIT)</text>
                <text x="24" y="48">AIR TRAFFIC CONTROL DISPATCHER</text>
                <text x="${width - 190}" y="32">INVENTORY: ACID ESCROW v1.0</text>
                <text x="${width - 190}" y="48">COORDINATE LOCK: ACTIVE</text>
            </g>
        `;

        // Render Flight Paths for tasks
        svgHtml += `<g class="flight-paths">`;
        this.tasks.forEach(task => {
            const pickup = this.findLandmark(task.pickup_location);
            const drop = this.findLandmark(task.drop_location);

            if (!pickup || !drop || pickup.id === drop.id) return;

            const isSelected = this.activeTaskId === task.task_id;
            const color = statusColors[task.status] || "#00e5ff";
            const strokeWidth = isSelected ? 3.5 : (task.status === "completed" ? 1.5 : 2.5);
            const opacity = isSelected ? 1 : (task.status === "completed" ? 0.35 : 0.85);

            // Calculate bezier control point with an aesthetic curve offset
            const midX = (pickup.x + drop.x) / 2;
            const midY = (pickup.y + drop.y) / 2;
            const dx = drop.x - pickup.x;
            const dy = drop.y - pickup.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            // perpendicular vector
            const normX = -dy / (dist || 1);
            const normY = dx / (dist || 1);
            const curveOffset = Math.min(dist * 0.22, 60);

            const cpX = midX + normX * curveOffset;
            const cpY = midY + normY * curveOffset;

            const pathD = `M ${pickup.x} ${pickup.y} Q ${cpX} ${cpY} ${drop.x} ${drop.y}`;
            const markerType = task.status === "completed" ? "arrow-completed" : (task.status === "assigned" ? "arrow-assigned" : "arrow-open");

            svgHtml += `
                <g class="task-path-group" data-task-id="${task.task_id}" style="cursor: pointer;">
                    <!-- Hit area -->
                    <path d="${pathD}" fill="none" stroke="transparent" stroke-width="20" />
                    <!-- Visual Flight Line -->
                    <path 
                        d="${pathD}" 
                        fill="none" 
                        stroke="${color}" 
                        stroke-width="${strokeWidth}" 
                        stroke-dasharray="${task.status === 'open' ? '6 4' : (task.status === 'assigned' ? '8 3' : '4 4')}"
                        class="${task.status !== 'completed' ? 'animated-flight-path' : ''}"
                        opacity="${opacity}"
                        marker-end="url(#${markerType})"
                    />
                    <!-- Errand Bounty Chip Badge along path midpoint -->
                    <g transform="translate(${cpX}, ${cpY})" class="flight-badge">
                        <rect x="-34" y="-12" width="68" height="22" rx="11" fill="#0b1324" stroke="${color}" stroke-width="1.2" opacity="0.95" />
                        <text x="0" y="3" fill="#ffffff" font-family="'JetBrains Mono', monospace" font-size="10" font-weight="600" text-anchor="middle">₹${Number(task.bounty).toFixed(0)}</text>
                    </g>
                </g>
            `;
        });
        svgHtml += `</g>`;

        // Render Landmark Nodes
        svgHtml += `<g class="landmarks">`;
        this.landmarks.forEach(node => {
            // Count active errands originating or dropping here
            const hasPickup = this.tasks.some(t => t.status !== 'completed' && t.status !== 'cancelled' && this.findLandmark(t.pickup_location)?.id === node.id);
            const hasDrop = this.tasks.some(t => t.status !== 'completed' && t.status !== 'cancelled' && this.findLandmark(t.drop_location)?.id === node.id);
            const isActiveNode = hasPickup || hasDrop;

            const ringColor = hasPickup ? "#00e5ff" : (hasDrop ? "#f59e0b" : "#334155");

            svgHtml += `
                <g class="landmark-node ${isActiveNode ? 'active-node' : ''}" transform="translate(${node.x}, ${node.y})" data-landmark-id="${node.id}">
                    <!-- Outer pulsating ring if active -->
                    ${isActiveNode ? `
                        <circle cx="0" cy="0" r="18" fill="none" stroke="${ringColor}" stroke-width="1.2" opacity="0.6" class="node-pulse" />
                        <circle cx="0" cy="0" r="26" fill="none" stroke="${ringColor}" stroke-width="0.8" opacity="0.3" class="node-pulse-outer" />
                    ` : ''}

                    <!-- Node Core Base -->
                    <circle cx="0" cy="0" r="12" fill="#0b1322" stroke="${ringColor}" stroke-width="2" />
                    <text x="0" y="4" font-size="10" text-anchor="middle">${node.icon}</text>

                    <!-- Text label -->
                    <rect x="-55" y="16" width="110" height="18" rx="4" fill="rgba(10, 18, 32, 0.85)" stroke="rgba(255,255,255,0.08)" stroke-width="0.5" />
                    <text x="0" y="29" fill="#e2e8f0" font-family="'Inter', sans-serif" font-size="9.5" font-weight="500" text-anchor="middle">${node.short}</text>
                </g>
            `;
        });
        svgHtml += `</g>`;

        this.svg.innerHTML = svgHtml;
        this.attachEventListeners();
    }

    attachEventListeners() {
        if (!this.svg) return;
        const pathGroups = this.svg.querySelectorAll('.task-path-group');
        pathGroups.forEach(el => {
            el.addEventListener('click', () => {
                const taskId = parseInt(el.getAttribute('data-task-id'));
                if (taskId) {
                    if (window.soundFX) window.soundFX.ping();
                    this.setActiveTask(taskId);
                    this.onTaskSelect(taskId);
                }
            });
        });
    }
}

window.CampusRadar = CampusRadar;
