/**
 * Lattice Lock Dashboard - Main Application
 * Handles WebSocket connection, state management, and UI coordination
 */

import { CONSTANTS, formatTime, escapeHtml } from './utils.js';
import { MetricsChart } from './components/metrics_chart.js';
import { ProjectCard } from './components/project_card.js';
import { AlertList } from './components/alert_list.js';

/**
 * Main dashboard application class.
 */
export class LatticeDashboard {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = CONSTANTS.MAX_RECONNECT_ATTEMPTS;
        this.reconnectDelay = CONSTANTS.RECONNECT_DELAY_MS;

        // WebSocket Heartbeat configuration
        this.heartbeatInterval = null;
        this.missedHeartbeats = 0;
        this.maxMissedHeartbeats = 3;

        this.state = {
            projects: [],
            metrics: {},
            alerts: [],
            connected: false
        };
        this.charts = {};
        this.boundRefresh = this.refresh.bind(this);
        this.init();
    }

    init() {
        this.bindEvents();
        this.initNavigation();
        this.connectWebSocket();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    bindEvents() {
        document.getElementById('refresh-btn').addEventListener('click', this.boundRefresh);
        document.getElementById('validate-all-btn').addEventListener('click', () => this.validateAll());
        document.getElementById('run-gauntlet-btn').addEventListener('click', () => this.runGauntlet());
        document.getElementById('rollback-btn').addEventListener('click', () => this.triggerRollback());
        document.getElementById('clear-alerts-btn').addEventListener('click', () => this.clearAlerts());
        document.getElementById('export-alerts-btn').addEventListener('click', () => this.exportAlerts());
        document.getElementById('status-filter').addEventListener('change', (e) => this.filterProjects(e.target.value));
        document.getElementById('time-range').addEventListener('change', (e) => this.updateTimeRange(e.target.value));
    }

    /**
     * Cleans up resources, event listeners, and intervals.
     */
    destroy() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.removeEventListener('click', this.boundRefresh);
        }

        if (this.autoRefreshInterval) clearInterval(this.autoRefreshInterval);
        this.stopHeartbeat();

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.showSection(section);
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            });
        });
    }

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionId}-section`).classList.add('active');

        if (sectionId === 'metrics') {
            this.initCharts();
        }
    }

    connectWebSocket() {
        const wsUrl = this.getWebSocketUrl();

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.state.connected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.startHeartbeat();
            };

            this.ws.onmessage = (event) => {
                try {
                    // Reset heartbeat counter on any message
                    this.missedHeartbeats = 0;

                    if (event.data === 'ping') {
                        this.ws.send('pong');
                        return;
                    }
                    if (event.data === 'pong') {
                        return;
                    }

                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error, event.data);
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.cleanupWebSocket();
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                // On error, we rely on onclose to handle reconnection
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
            this.attemptReconnect(); // Ensure we retry even on initial connection failure
        }
    }

    cleanupWebSocket() {
        this.state.connected = false;
        this.updateConnectionStatus(false);
        this.stopHeartbeat();
    }

    startHeartbeat() {
        this.stopHeartbeat();
        this.missedHeartbeats = 0;
        this.heartbeatInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
                this.missedHeartbeats++;
                if (this.missedHeartbeats > this.maxMissedHeartbeats) {
                    console.warn(`Missed ${this.missedHeartbeats} heartbeats, reconnecting...`);
                    this.ws.close(); // This will trigger onclose and reconnection
                }
            }
        }, 30000); // 30s heartbeat
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:8080';
        return `${protocol}//${host}/dashboard/live`;
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            // Exponential backoff
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms...`);
            setTimeout(() => this.connectWebSocket(), delay);
        }
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        const dot = statusEl.querySelector('.status-dot');

        if (connected) {
            dot.classList.remove('disconnected');
            dot.classList.add('connected');
            statusEl.innerHTML = '<span class="status-dot connected"></span> Connected';
        } else {
            dot.classList.remove('connected');
            dot.classList.add('disconnected');
            statusEl.innerHTML = '<span class="status-dot disconnected"></span> Disconnected';
        }
    }

    handleMessage(message) {
        switch (message.type) {
            case 'projects_update':
                this.updateProjects(message.data);
                break;
            case 'metrics_update':
                this.updateMetrics(message.data);
                break;
            case 'alert':
                this.addAlert(message.data);
                break;
            case 'project_status_change':
                this.handleProjectStatusChange(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    async loadInitialData() {
        try {
            const [projectsRes, metricsRes, alertsRes] = await Promise.all([
                this.fetchData('/api/projects'),
                this.fetchData('/api/metrics'),
                this.fetchData('/api/alerts')
            ]);

            if (projectsRes) this.updateProjects(projectsRes);
            if (metricsRes) this.updateMetrics(metricsRes);
            if (alertsRes) this.state.alerts = alertsRes;

            this.renderAlerts();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.loadMockData();
        }
    }

    async fetchData(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.warn(`Failed to fetch ${endpoint}:`, error.message);
            throw error; // Re-throw to be caught by loadInitialData or caller
        }
    }

    loadMockData() {
        const mockProjects = [
            { id: 1, name: 'api-service', status: 'healthy', lastValidation: new Date().toISOString(), entities: 4, constraints: 12 },
            { id: 2, name: 'data-pipeline', status: 'healthy', lastValidation: new Date().toISOString(), entities: 6, constraints: 18 },
            { id: 3, name: 'auth-service', status: 'warning', lastValidation: new Date().toISOString(), entities: 3, constraints: 8 },
            { id: 4, name: 'notification-service', status: 'error', lastValidation: new Date().toISOString(), entities: 2, constraints: 5 }
        ];

        const mockMetrics = {
            validations: { passed: 156, failed: 12, warnings: 23 },
            modelUsage: { 'gpt-4': 45, 'claude-3': 32, 'gemini-pro': 18, 'llama-3': 5 },
            responseTimes: [120, 145, 98, 167, 134, 112, 156],
            errorRates: [0.02, 0.03, 0.01, 0.04, 0.02, 0.01, 0.03]
        };

        const mockAlerts = [
            { id: 1, type: 'error', title: 'Validation Failed', message: 'auth-service failed schema validation', time: new Date(Date.now() - 300000).toISOString() },
            { id: 2, type: 'warning', title: 'High Latency', message: 'Model response time exceeded threshold', time: new Date(Date.now() - 600000).toISOString() },
            { id: 3, type: 'info', title: 'Deployment Complete', message: 'api-service v2.1.0 deployed successfully', time: new Date(Date.now() - 900000).toISOString() }
        ];

        this.updateProjects(mockProjects);
        this.updateMetrics(mockMetrics);
        this.state.alerts = mockAlerts;
        this.renderAlerts();
    }

    updateProjects(projects) {
        this.state.projects = projects;
        this.renderProjects();
        this.updateStats();
    }

    updateMetrics(metrics) {
        this.state.metrics = metrics;
        this.updateCharts();
    }

    renderProjects() {
        const container = document.getElementById('projects-list');
        container.innerHTML = '';

        this.state.projects.forEach(project => {
            const card = ProjectCard.create(project, {
                onValidate: () => this.validateProject(project.id),
                onRollback: () => this.rollbackProject(project.id)
            });
            container.appendChild(card);
        });
    }

    updateStats() {
        const projects = this.state.projects;
        const total = projects.length;
        const healthy = projects.filter(p => p.status === 'healthy').length;
        const warning = projects.filter(p => p.status === 'warning').length;
        const error = projects.filter(p => p.status === 'error').length;

        document.getElementById('total-projects').textContent = total;
        document.getElementById('healthy-projects').textContent = healthy;
        document.getElementById('warning-projects').textContent = warning;
        document.getElementById('error-projects').textContent = error;

        this.updateRecentActivity();
    }

    updateRecentActivity() {
        const container = document.getElementById('recent-activity');
        const activities = this.state.projects
            .map(p => ({
                message: `${p.name} - ${p.status}`,
                time: p.lastValidation
            }))
            .sort((a, b) => new Date(b.time) - new Date(a.time))
            .slice(0, 5);

        // Clear existing content
        container.innerHTML = '';

        // Safely render recent activity items without using innerHTML for untrusted data
        activities.forEach(activity => {
            const item = document.createElement('div');
            item.className = 'activity-item';

            const messageEl = document.createElement('div');
            messageEl.textContent = activity.message;

            const timeEl = document.createElement('div');
            timeEl.className = 'activity-time';
            timeEl.textContent = formatTime(activity.time);

            item.appendChild(messageEl);
            item.appendChild(timeEl);
            container.appendChild(item);
        });
    }

    initCharts() {
        if (Object.keys(this.charts).length === 0) {
            this.charts.validation = MetricsChart.createDoughnut('validation-chart', 'Validation Results');
            this.charts.modelUsage = MetricsChart.createBar('model-usage-chart', 'Model Usage');
            this.charts.responseTime = MetricsChart.createLine('response-time-chart', 'Response Times (ms)');
            this.charts.errorRate = MetricsChart.createLine('error-rate-chart', 'Error Rate (%)');
        }
        this.updateCharts();
    }

    updateCharts() {
        const metrics = this.state.metrics;
        if (!metrics || Object.keys(metrics).length === 0) return;

        if (this.charts.validation && metrics.validations) {
            MetricsChart.updateDoughnut(this.charts.validation, metrics.validations);
        }
        if (this.charts.modelUsage && metrics.modelUsage) {
            MetricsChart.updateBar(this.charts.modelUsage, metrics.modelUsage);
        }
        if (this.charts.responseTime && metrics.responseTimes) {
            MetricsChart.updateLine(this.charts.responseTime, metrics.responseTimes, 'Response Time');
        }
        if (this.charts.errorRate && metrics.errorRates) {
            MetricsChart.updateLine(this.charts.errorRate, metrics.errorRates.map(r => r * 100), 'Error Rate');
        }
    }

    addAlert(alert) {
        this.state.alerts.unshift(alert);
        AlertList.addAlert(alert);
    }

    renderAlerts() {
        const container = document.getElementById('alerts-list');
        container.innerHTML = '';
        this.state.alerts.forEach(alert => {
            container.appendChild(AlertList.createAlertElement(alert));
        });
    }

    handleProjectStatusChange(data) {
        const project = this.state.projects.find(p => p.id === data.projectId);
        if (project) {
            project.status = data.newStatus;
            this.renderProjects();
            this.updateStats();

            const card = document.querySelector(`[data-project-id="${data.projectId}"]`);
            if (card) {
                card.classList.add('highlight');
                setTimeout(() => card.classList.remove('highlight'), 1000);
            }
        }
    }

    filterProjects(status) {
        const cards = document.querySelectorAll('.project-card');
        cards.forEach(card => {
            if (status === 'all' || card.dataset.status === status) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    updateTimeRange(range) {
        console.log('Updating time range to:', range);
        this.loadInitialData();
    }

    /**
     * Refreshes the dashboard data.
     * @returns {Promise<void>}
     */
    async refresh() {
        await this.loadInitialData();
    }

    validateAll() {
        console.log('Validating all projects...');
        this.addAlert({
            id: Date.now(),
            type: 'info',
            title: 'Validation Started',
            message: 'Running validation on all projects',
            time: new Date().toISOString()
        });
    }

    runGauntlet() {
        console.log('Running Gauntlet tests...');
        this.addAlert({
            id: Date.now(),
            type: 'info',
            title: 'Gauntlet Started',
            message: 'Running Gauntlet test suite',
            time: new Date().toISOString()
        });
    }

    triggerRollback() {
        if (confirm('Are you sure you want to trigger a rollback?')) {
            console.log('Triggering rollback...');
            this.addAlert({
                id: Date.now(),
                type: 'warning',
                title: 'Rollback Initiated',
                message: 'System rollback has been triggered',
                time: new Date().toISOString()
            });
        }
    }

    validateProject(projectId) {
        console.log('Validating project:', projectId);
    }

    rollbackProject(projectId) {
        console.log('Rolling back project:', projectId);
    }

    clearAlerts() {
        this.state.alerts = [];
        document.getElementById('alerts-list').innerHTML = '';
    }

    exportAlerts() {
        const data = JSON.stringify(this.state.alerts, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `alerts-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    startAutoRefresh() {
        this.autoRefreshInterval = setInterval(() => {
            // Only auto-refresh if valid WebSocket connection is not active
            // or as a backup to keep non-realtime data fresh
            if (!this.state.connected) {
                this.loadInitialData();
            }
        }, CONSTANTS.AUTO_REFRESH_INTERVAL_MS);
    }
}
