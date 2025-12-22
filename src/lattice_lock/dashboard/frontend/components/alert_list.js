export default class AlertList {
    constructor(containerElement) {
        this.container = containerElement;
    }

    addAlert(alert) {
        const alertEl = document.createElement('div');
        alertEl.className = 'alert-item';

        const severityClass = this.getSeverityClass(alert.severity);

        // Build DOM nodes explicitly to avoid injecting untrusted data via innerHTML
        const alertContent = document.createElement('div');
        alertContent.className = 'alert-content';

        const alertTitle = document.createElement('div');
        alertTitle.className = 'alert-title';
        alertTitle.textContent = alert.message != null ? String(alert.message) : '';

        const alertTime = document.createElement('div');
        alertTime.className = 'alert-time';
        alertTime.textContent = alert.timestamp
            ? new Date(alert.timestamp).toLocaleString()
            : '';

        alertContent.appendChild(alertTitle);
        alertContent.appendChild(alertTime);

        const alertSeverity = document.createElement('div');
        alertSeverity.className = 'alert-severity';
        if (severityClass) {
            alertSeverity.classList.add(severityClass);
        }
        alertSeverity.textContent = alert.severity != null ? String(alert.severity) : '';

        alertEl.appendChild(alertContent);
        alertEl.appendChild(alertSeverity);

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
