/**
 * Alert List Component
 * Scrollable list of recent alerts with visual indicators
 * @namespace AlertList
 */

import { formatTime, escapeHtml } from '../utils.js';

export const AlertList = {
    /**
     * Creates an alert DOM element.
     * @param {Object} alert - Alert data.
     * @returns {HTMLElement} The alert element.
     */
    createAlertElement(alert) {
        const element = document.createElement('div');
        element.className = 'alert-item';
        element.dataset.alertId = alert.id;

        const iconClass = this.getIconClass(alert.type);
        const icon = this.getIcon(alert.type);

        element.innerHTML = `
            <div class="alert-icon ${iconClass}">
                ${icon}
            </div>
            <div class="alert-content">
                <div class="alert-title">${escapeHtml(alert.title)}</div>
                <div class="alert-message">${escapeHtml(alert.message)}</div>
                <div class="alert-time">${formatTime(alert.time)}</div>
            </div>
            <button class="alert-dismiss" title="Dismiss">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
        `;

        const dismissBtn = element.querySelector('.alert-dismiss');
        dismissBtn.addEventListener('click', () => this.dismiss(element));

        return element;
    },

    /**
     * Adds an alert to the list with animation.
     * @param {Object} alert - Alert data.
     */
    addAlert(alert) {
        const container = document.getElementById('alerts-list');
        if (!container) return;

        const element = this.createAlertElement(alert);
        element.classList.add('new');

        container.insertBefore(element, container.firstChild);

        setTimeout(() => element.classList.remove('new'), 300);

        this.showNotification(alert);
    },

    /**
     * Dismisses an alert element.
     * @param {HTMLElement} element - The alert element to dismiss.
     */
    dismiss(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateX(100%)';
        element.style.transition = 'all 0.3s ease-out';

        setTimeout(() => element.remove(), 300);
    },

    /**
     * Gets the CSS class for a given alert type.
     * @param {string} type - Alert type.
     * @returns {string} CSS class name.
     */
    getIconClass(type) {
        const classes = {
            error: 'error',
            warning: 'warning',
            info: 'info',
            success: 'success'
        };
        return classes[type] || 'info';
    },

    /**
     * Gets the SVG icon for a given alert type.
     * @param {string} type - Alert type.
     * @returns {string} SVG string.
     */
    getIcon(type) {
        const icons = {
            error: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>',
            warning: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
            info: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
            success: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>'
        };
        return icons[type] || icons.info;
    },

    /**
     * Shows a browser notification for the alert.
     * @param {Object} alert - Alert data.
     */
    showNotification(alert) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(alert.title, {
                body: alert.message,
                icon: '/favicon.ico'
            });
        }
    },

    /**
     * Requests permission for browser notifications.
     */
    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    },

    /**
     * Filters alerts by type.
     * @param {string} type - Filter type.
     */
    filterByType(type) {
        const alerts = document.querySelectorAll('.alert-item');
        alerts.forEach(alert => {
            const iconEl = alert.querySelector('.alert-icon');
            if (type === 'all' || iconEl.classList.contains(type)) {
                alert.style.display = 'flex';
            } else {
                alert.style.display = 'none';
            }
        });
    },

    /**
     * Clears all alerts from the list.
     */
    clearAll() {
        const container = document.getElementById('alerts-list');
        if (container) {
            container.innerHTML = '';
        }
    },

    /**
     * Exports alerts to a JSON string.
     * @returns {string} JSON string of alerts.
     */
    exportToJson() {
        const alerts = [];
        document.querySelectorAll('.alert-item').forEach(el => {
            alerts.push({
                id: el.dataset.alertId,
                title: el.querySelector('.alert-title').textContent,
                message: el.querySelector('.alert-message').textContent,
                time: el.querySelector('.alert-time').textContent
            });
        });
        return JSON.stringify(alerts, null, 2);
    }
};
