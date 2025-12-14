import ProjectCard from './components/project-card.js';
import MetricsChart from './components/metrics-chart.js';
import AlertList from './components/alert-list.js';

class DashboardApp {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 3000;
        this.projectList = document.getElementById('project-list');
        this.alertList = new AlertList(document.getElementById('alert-list'));
        this.metricsChart = new MetricsChart(document.getElementById('metrics-chart'));

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        // For development/testing if not served from backend
        // const wsUrl = 'ws://localhost:8080/ws';

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.updateConnectionStatus(true);
            console.log('Connected to Dashboard Backend');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };

        this.ws.onclose = () => {
            this.updateConnectionStatus(false);
            console.log('Disconnected. Reconnecting in 3s...');
            setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.ws.close();
        };
    }

    handleMessage(message) {
        switch (message.type) {
            case 'initial_state':
            case 'update':
                this.updateDashboard(message.data);
                break;
            case 'alert':
                this.alertList.addAlert(message.data);
                break;
            default:
                console.warn('Unknown message type:', message.type);
        }
    }

    updateDashboard(data) {
        if (data.projects) {
            this.renderProjects(data.projects);
            document.getElementById('total-projects-count').textContent = data.projects.length;
        }

        if (data.metrics) {
            this.metricsChart.update(data.metrics);
        }

        if (data.system_health) {
            document.getElementById('system-health-score').textContent = `${data.system_health}%`;
        }

        if (data.active_alerts_count !== undefined) {
            document.getElementById('active-alerts-count').textContent = data.active_alerts_count;
        }
    }

    renderProjects(projects) {
        this.projectList.innerHTML = '';
        projects.forEach(project => {
            const card = new ProjectCard(project);
            this.projectList.appendChild(card.render());
        });
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (connected) {
            statusEl.textContent = 'Connected';
            statusEl.classList.remove('disconnected');
            statusEl.classList.add('connected');
        } else {
            statusEl.textContent = 'Disconnected';
            statusEl.classList.remove('connected');
            statusEl.classList.add('disconnected');
        }
    }

    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', () => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'request_update' }));
            }
        });

        document.getElementById('trigger-rollback-btn').addEventListener('click', () => {
            if (confirm('Are you sure you want to trigger a manual rollback?')) {
                // In a real app, this would be an API call
                console.log('Triggering rollback...');
                // fetch('/api/rollback', { method: 'POST' });
            }
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();
});
