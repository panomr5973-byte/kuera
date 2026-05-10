/**
 * KUWERA Admin Panel Controller
 * Main JavaScript for panel interactions and data management
 */

// Global state
const AppState = {
    currentPanel: 'dashboard',
    models: [],
    interactions: [],
    syncHistory: [],
    systemHistory: [],
    uptime: 0,
    charts: {}
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initLoadingScreen();
    initNavigation();
    initData();
    initCharts();
    initEventListeners();
    startUptimeCounter();
    
    // Simulate loading
    setTimeout(() => {
        hideLoadingScreen();
    }, 2000);
});

// Loading Screen
function initLoadingScreen() {
    const progress = document.getElementById('loading-progress');
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 100) {
            clearInterval(interval);
        } else {
            width += Math.random() * 15;
            if (width > 100) width = 100;
            progress.style.width = width + '%';
        }
    }, 100);
}

function hideLoadingScreen() {
    const loading = document.getElementById('loading-screen');
    const app = document.getElementById('app');
    
    loading.style.opacity = '0';
    setTimeout(() => {
        loading.style.display = 'none';
        app.classList.remove('hidden');
    }, 500);
}

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const panelId = item.dataset.panel;
            switchPanel(panelId);
            
            // Update active state
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchPanel(panelId) {
    // Hide all panels
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show target panel
    const targetPanel = document.getElementById(`panel-${panelId}`);
    if (targetPanel) {
        targetPanel.classList.add('active');
        AppState.currentPanel = panelId;
        
        // Refresh panel-specific data
        refreshPanelData(panelId);
    }
}

function refreshPanelData(panelId) {
    switch(panelId) {
        case 'evolution':
            loadEvolutionData();
            break;
        case 'models':
            loadModelsData();
            break;
        case 'interactions':
            loadInteractionsData();
            break;
        case 'paths':
            loadPathsData();
            break;
        case 'sync':
            loadSyncData();
            break;
        case 'history':
            loadHistoryData();
            break;
    }
}

// Data Initialization
function initData() {
    // Load models data
    AppState.models = [
        { id: 'model_20260402_100050', type: 'rf', f1: 0.643, accuracy: 0.75, samples: 20, date: '2026-04-02', production: false },
        { id: 'model_20260402_113959', type: 'rf', f1: 0.527, accuracy: 0.662, samples: 1094, date: '2026-04-02', production: false },
        { id: 'model_20260402_115503', type: 'gb', f1: 0.673, accuracy: 0.673, samples: 145580, date: '2026-04-02', production: true },
        { id: 'model_20260402_121344', type: 'gb', f1: 0.638, accuracy: 0.661, samples: 414483, date: '2026-04-02', production: false },
        { id: 'model_20260402_135212', type: 'gb', f1: 0.629, accuracy: 0.656, samples: 388036, date: '2026-04-02', production: false },
        { id: 'model_20260402_150537', type: 'gb', f1: 0.643, accuracy: 0.662, samples: 367033, date: '2026-04-02', production: false }
    ];
    
    // Load interactions
    AppState.interactions = [
        { type: 'chat', user: 'User #42', message: 'Apa itu KUWERA?', time: '2 menit yang lalu', sentiment: 'positive' },
        { type: 'api', user: 'System', message: 'Model prediction request: 0.85 confidence', time: '5 menit yang lalu', sentiment: 'neutral' },
        { type: 'chat', user: 'User #128', message: 'Terima kasih atas bantuannya!', time: '12 menit yang lalu', sentiment: 'positive' },
        { type: 'voice', user: 'User #85', message: 'Voice query processed (3.2s)', time: '15 menit yang lalu', sentiment: 'neutral' },
        { type: 'chat', user: 'User #256', message: 'Bagaimana cara kerja AI ini?', time: '23 menit yang lalu', sentiment: 'curious' },
        { type: 'api', user: 'Scheduler', message: 'Daily maintenance completed', time: '1 jam yang lalu', sentiment: 'success' }
    ];
    
    // Load sync history
    AppState.syncHistory = [
        { time: '2026-04-09 13:08:10', status: 'success', files: 10, size: '0 MB' },
        { time: '2026-04-09 02:00:00', status: 'success', files: 10, size: '0 MB' },
        { time: '2026-04-08 02:00:00', status: 'success', files: 8, size: '7.2 GB' },
        { time: '2026-04-07 02:00:00', status: 'success', files: 6, size: '3.1 GB' },
        { time: '2026-04-06 02:00:00', status: 'warning', files: 5, size: '2.8 GB', note: 'Partial sync' }
    ];
    
    // Load system history
    AppState.systemHistory = [
        { time: '2026-04-09 13:08:10', event: 'Daily maintenance completed', type: 'sync', detail: 'All systems synchronized' },
        { time: '2026-04-09 12:00:00', event: 'HF Models archived to D:', type: 'model', detail: 'Moved 7.2 GB to AI-Models-Archive' },
        { time: '2026-04-09 10:30:00', event: 'New admin panel initialized', type: 'system', detail: 'KUWERA Admin Panel v1.0' },
        { time: '2026-04-08 09:14:18', event: 'Scheduler crash detected', type: 'error', detail: 'Auto-recovery successful' },
        { time: '2026-04-02 11:55:00', event: 'MEGA EVOLUTION achieved', type: 'model', detail: 'F1 Score 0.673 reached' },
        { time: '2026-04-02 10:00:00', event: 'First model created', type: 'model', detail: 'Genesis - 20 samples' }
    ];
}

// Charts
function initCharts() {
    // Evolution Chart
    const evolutionCtx = document.getElementById('evolution-chart');
    if (evolutionCtx) {
        AppState.charts.evolution = new Chart(evolutionCtx, {
            type: 'line',
            data: {
                labels: ['Gen 1', 'Gen 2', 'Gen 3', 'Gen 4', 'Gen 5', 'Gen 6'],
                datasets: [{
                    label: 'F1 Score',
                    data: [0.643, 0.527, 0.673, 0.638, 0.629, 0.643],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Accuracy',
                    data: [0.75, 0.662, 0.673, 0.661, 0.656, 0.662],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#8a8a9a' }
                    }
                },
                scales: {
                    y: {
                        grid: { color: '#2a2a3a' },
                        ticks: { color: '#8a8a9a' }
                    },
                    x: {
                        grid: { color: '#2a2a3a' },
                        ticks: { color: '#8a8a9a' }
                    }
                }
            }
        });
    }
    
    // Interaction Chart
    const interactionCtx = document.getElementById('interaction-chart');
    if (interactionCtx) {
        AppState.charts.interaction = new Chart(interactionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Chat', 'API', 'Voice', 'File Upload'],
                datasets: [{
                    data: [65, 20, 10, 5],
                    backgroundColor: [
                        '#00d4ff',
                        '#7b2dff',
                        '#00ff88',
                        '#ff2d7b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#8a8a9a' }
                    }
                }
            }
        });
    }
}

// Event Listeners
function initEventListeners() {
    // Avatar controls
    const btnSpeak = document.getElementById('btn-speak');
    const btnListen = document.getElementById('btn-listen');
    const btnAnimate = document.getElementById('btn-animate');
    const chatInput = document.getElementById('avatar-chat-input');
    const btnSend = document.getElementById('btn-send-chat');
    
    if (btnSpeak) {
        btnSpeak.addEventListener('click', () => {
            if (window.avatar3D) {
                window.avatar3D.speak("Hello, I am KUWERA, your Indonesian AI assistant. I am ready to help you with any questions about AI evolution and development.");
            }
        });
    }
    
    if (btnListen) {
        btnListen.addEventListener('click', () => {
            if (window.avatar3D) {
                window.avatar3D.listen();
            }
        });
    }
    
    if (btnAnimate) {
        btnAnimate.addEventListener('click', () => {
            if (window.avatar3D) {
                // Trigger special animation
                window.avatar3D.speak("Animation sequence initiated. I am fully operational and ready to assist.");
            }
        });
    }
    
    if (btnSend && chatInput) {
        const sendChat = () => {
            const text = chatInput.value.trim();
            if (text) {
                // Add user message
                if (window.avatar3D) {
                    window.avatar3D.addChatMessage(text, 'user');
                }
                
                // Simulate AI response
                setTimeout(() => {
                    if (window.avatar3D) {
                        const responses = [
                            "I understand. Let me analyze that for you.",
                            "Interesting question! Based on my training data, I can help with that.",
                            "Processing your request...",
                            "As an AI trained on Indonesian data, I can provide insights on that topic."
                        ];
                        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                        window.avatar3D.speak(randomResponse);
                    }
                }, 1000);
                
                chatInput.value = '';
            }
        };
        
        btnSend.addEventListener('click', sendChat);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChat();
        });
    }
    
    // Interaction filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterInteractions(btn.dataset.filter);
        });
    });
}

// Panel Data Loaders
function loadEvolutionData() {
    const container = document.getElementById('evolution-timeline-content');
    if (!container) return;
    
    const phases = [
        { phase: 'inception', name: 'Inception', model: 'model_20260402_100050', f1: 0.643, samples: 20, status: 'completed' },
        { phase: 'toddler', name: 'Toddler', model: 'model_20260402_113959', f1: 0.527, samples: 1094, status: 'completed' },
        { phase: 'adolescent', name: 'Adolescent', model: 'model_20260402_115503', f1: 0.673, samples: 145580, status: 'active' },
        { phase: 'nusantara', name: 'Nusantara', model: 'model_20260402_121344', f1: 0.638, samples: 414483, status: 'current' }
    ];
    
    container.innerHTML = phases.map(p => `
        <div class="timeline-item">
            <span class="phase-badge ${p.phase}">${p.name}</span>
            <span>${p.model}</span>
            <span>F1: ${p.f1} | Samples: ${p.samples.toLocaleString()}</span>
            <span class="status-badge ${p.status}">${p.status.toUpperCase()}</span>
        </div>
    `).join('');
}

function loadModelsData() {
    const container = document.getElementById('models-grid');
    if (!container) return;
    
    container.innerHTML = AppState.models.map(m => `
        <div class="model-card ${m.production ? 'production' : ''}">
            <div class="model-header">
                <span class="model-name">${m.id}</span>
                <span class="model-type">${m.type.toUpperCase()}</span>
            </div>
            <div class="model-metrics">
                <div class="metric">
                    <span class="metric-value">${m.f1}</span>
                    <span class="metric-label">F1 Score</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${(m.accuracy * 100).toFixed(1)}%</span>
                    <span class="metric-label">Accuracy</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${(m.samples / 1000).toFixed(1)}K</span>
                    <span class="metric-label">Samples</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${m.date}</span>
                    <span class="metric-label">Created</span>
                </div>
            </div>
        </div>
    `).join('');
}

function loadInteractionsData() {
    const container = document.getElementById('interaction-log');
    if (!container) return;
    
    const icons = {
        chat: '💬',
        voice: '🎤',
        api: '⚡'
    };
    
    container.innerHTML = AppState.interactions.map(i => `
        <div class="interaction-item" data-type="${i.type}">
            <div class="interaction-type ${i.type}">${icons[i.type]}</div>
            <div class="interaction-content">
                <div class="interaction-meta">
                    <span class="interaction-user">${i.user}</span>
                    <span class="interaction-time">${i.time}</span>
                </div>
                <div class="interaction-message">${i.message}</div>
            </div>
        </div>
    `).join('');
}

function filterInteractions(type) {
    const items = document.querySelectorAll('.interaction-item');
    items.forEach(item => {
        if (type === 'all' || item.dataset.type === type) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function loadPathsData() {
    const cPaths = document.getElementById('c-paths');
    const dPaths = document.getElementById('d-paths');
    
    const cFolders = [
        'C:/AI-Project/models',
        'C:/AI-Project/logs',
        'C:/AI-Project/data',
        'C:/AI-Project/src',
        'C:/AI-Project/mlflow.db'
    ];
    
    const dFolders = [
        'D:/AI-Backup-2026/models',
        'D:/AI-Models-Archive/models',
        'D:/DataKlien',
        'D:/AI-Backup-2026/logs'
    ];
    
    if (cPaths) {
        cPaths.innerHTML = cFolders.map(f => `
            <div class="path-item">${f}</div>
        `).join('');
    }
    
    if (dPaths) {
        dPaths.innerHTML = dFolders.map(f => `
            <div class="path-item">${f}</div>
        `).join('');
    }
}

function loadSyncData() {
    const container = document.getElementById('sync-log');
    if (!container) return;
    
    // Add history list after the h3
    const historyHtml = `
        <div class="sync-history-list" style="margin-top: 20px;">
            ${AppState.syncHistory.map(h => `
                <div class="sync-history-item" style="padding: 15px; border-bottom: 1px solid #2a2a3a; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="color: #00d4ff; font-family: 'Orbitron', sans-serif;">${h.time}</div>
                        <div style="color: #8a8a9a; font-size: 0.85rem;">${h.files} files • ${h.size}</div>
                        ${h.note ? `<div style="color: #ffaa00; font-size: 0.8rem;">⚠ ${h.note}</div>` : ''}
                    </div>
                    <span class="status-badge" style="background: ${h.status === 'success' ? 'rgba(0,255,136,0.1)' : 'rgba(255,170,0,0.1)'}; color: ${h.status === 'success' ? '#00ff88' : '#ffaa00'};">
                        ${h.status.toUpperCase()}
                    </span>
                </div>
            `).join('')}
        </div>
    `;
    
    const existingList = container.querySelector('.sync-history-list');
    if (existingList) {
        existingList.remove();
    }
    container.insertAdjacentHTML('beforeend', historyHtml);
}

function loadHistoryData() {
    const container = document.getElementById('history-timeline');
    if (!container) return;
    
    const typeColors = {
        model: '#00d4ff',
        sync: '#00ff88',
        error: '#ff4444',
        system: '#7b2dff'
    };
    
    container.innerHTML = AppState.systemHistory.map(h => `
        <div class="history-item">
            <div class="history-time">${h.time}</div>
            <div class="history-content">
                <h4>${h.event}</h4>
                <p>${h.detail}</p>
                <span class="history-tag ${h.type}" style="color: ${typeColors[h.type]}">${h.type.toUpperCase()}</span>
            </div>
        </div>
    `).join('');
}

// Quick Actions
function syncModels() {
    alert('Syncing models... Check console for details');
    // In real implementation, this would call the Python sync script
}

function retrainModel() {
    if (confirm('Start model retraining? This may take several minutes.')) {
        alert('Retraining initiated. Check Models panel for progress.');
    }
}

function backupData() {
    alert('Backup started. Data will be synced to D: drive.');
}

function cleanLogs() {
    if (confirm('Clean logs older than 30 days?')) {
        alert('Log cleanup completed.');
    }
}

// Uptime Counter
function startUptimeCounter() {
    const counter = document.getElementById('uptime-counter');
    if (!counter) return;
    
    setInterval(() => {
        AppState.uptime++;
        const hours = Math.floor(AppState.uptime / 3600).toString().padStart(2, '0');
        const minutes = Math.floor((AppState.uptime % 3600) / 60).toString().padStart(2, '0');
        const seconds = (AppState.uptime % 60).toString().padStart(2, '0');
        counter.textContent = `${hours}:${minutes}:${seconds}`;
    }, 1000);
}

// Real-time updates (simulated)
setInterval(() => {
    // Update stats randomly
    const interactions = document.getElementById('stat-interactions');
    if (interactions && Math.random() > 0.7) {
        const current = parseInt(interactions.textContent.replace(/,/g, ''));
        interactions.textContent = (current + Math.floor(Math.random() * 5)).toLocaleString();
    }
}, 5000);

// Export for global access
window.switchPanel = switchPanel;
window.syncModels = syncModels;
window.retrainModel = retrainModel;
window.backupData = backupData;
window.cleanLogs = cleanLogs;
