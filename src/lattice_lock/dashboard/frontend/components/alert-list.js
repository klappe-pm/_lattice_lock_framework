export default class AlertList {
    constructor(containerElement) {
        this.container = containerElement;
    }

    addAlert(alert) {
        const alertEl = document.createElement('div');
        alertEl.className = 'alert-item';

        const severityClass = this.getSeverityClass(alert.severity);

        alertEl.innerHTML = `
            <div class="alert-content">
                <div class="alert-title">${alert.message}</div>
                <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
            </div>
            <div class="alert-severity ${severityClass}">${alert.severity}</div>
        `;

        // Add to top
        this.container.insertBefore(alertEl, this.container.firstChild);

        // Limit to 50 items
        if (this.container.children.length > 50) {
            this.container.removeChild(this.container.lastChild);
        }
    }

    getSeverityClass(severity) {
        switch (severity.toLowerCase()) {
            case 'critical':
            case 'error':
                return 'severity-critical';
            case 'warning':
                return 'severity-warning';
            default:
                return '';
        }
    }
}
