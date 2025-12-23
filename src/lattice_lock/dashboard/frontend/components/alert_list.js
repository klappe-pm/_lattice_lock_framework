/**
 * Alert List Component
 * Scrollable list of recent alerts with visual indicators
 */

const AlertList = {
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
                <div class="alert-title">${this.escapeHtml(alert.title)}</div>
                <div class="alert-message">${this.escapeHtml(alert.message)}</div>
                <div class="alert-time">${this.formatTime(alert.time)}</div>
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

    addAlert(alert) {
        const container = document.getElementById('alerts-list');
        if (!container) return;

        const element = this.createAlertElement(alert);
        element.classList.add('new');

        container.insertBefore(element, container.firstChild);

        setTimeout(() => element.classList.remove('new'), 300);

        this.showNotification(alert);
    },

    dismiss(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateX(100%)';
        element.style.transition = 'all 0.3s ease-out';

        setTimeout(() => element.remove(), 300);
    },

    getIconClass(type) {
        const classes = {
            error: 'error',
            warning: 'warning',
            info: 'info',
            success: 'success'
        };
        return classes[type] || 'info';
    },

    getIcon(type) {
        const icons = {
            error: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>',
            warning: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
            info: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
            success: '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>'
        };
        return icons[type] || icons.info;
    },

    formatTime(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },

    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    showNotification(alert) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(alert.title, {
                body: alert.message,
                icon: '/favicon.ico'
            });
        }
    },

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    },

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

    clearAll() {
        const container = document.getElementById('alerts-list');
        if (container) {
            container.innerHTML = '';
        }
    },

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

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlertList;
}
