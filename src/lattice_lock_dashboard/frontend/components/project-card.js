/**
 * Project Card Component
 * Displays project status with health indicator and actions
 */

const ProjectCard = {
    create(project, callbacks = {}) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.projectId = project.id;
        card.dataset.status = project.status;

        const statusIcon = this.getStatusIcon(project.status);
        const statusClass = project.status;

        card.innerHTML = `
            <div class="project-header">
                <span class="project-name">${this.escapeHtml(project.name)}</span>
                <span class="project-status ${statusClass}">
                    ${statusIcon}
                    ${this.capitalizeFirst(project.status)}
                </span>
            </div>
            <div class="project-details">
                <div class="project-detail">
                    <span>Entities</span>
                    <span>${project.entities || 0}</span>
                </div>
                <div class="project-detail">
                    <span>Constraints</span>
                    <span>${project.constraints || 0}</span>
                </div>
                <div class="project-detail">
                    <span>Last Validation</span>
                    <span>${this.formatTime(project.lastValidation)}</span>
                </div>
            </div>
            <div class="project-actions">
                <button class="btn btn-secondary btn-sm validate-btn">Validate</button>
                <button class="btn btn-secondary btn-sm details-btn">Details</button>
                ${project.status === 'error' ? '<button class="btn btn-danger btn-sm rollback-btn">Rollback</button>' : ''}
            </div>
        `;

        const validateBtn = card.querySelector('.validate-btn');
        if (validateBtn && callbacks.onValidate) {
            validateBtn.addEventListener('click', callbacks.onValidate);
        }

        const rollbackBtn = card.querySelector('.rollback-btn');
        if (rollbackBtn && callbacks.onRollback) {
            rollbackBtn.addEventListener('click', callbacks.onRollback);
        }

        const detailsBtn = card.querySelector('.details-btn');
        if (detailsBtn) {
            detailsBtn.addEventListener('click', () => this.showDetails(project));
        }

        return card;
    },

    getStatusIcon(status) {
        const icons = {
            healthy: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
            warning: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
            error: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>'
        };
        return icons[status] || icons.healthy;
    },

    formatTime(isoString) {
        if (!isoString) return 'Never';
        const date = new Date(isoString);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    },

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    showDetails(project) {
        console.log('Showing details for project:', project);
        alert(`Project: ${project.name}\nStatus: ${project.status}\nEntities: ${project.entities}\nConstraints: ${project.constraints}`);
    },

    highlight(card) {
        card.classList.add('highlight');
        setTimeout(() => card.classList.remove('highlight'), 1000);
    },

    updateStatus(card, newStatus) {
        card.dataset.status = newStatus;
        const statusEl = card.querySelector('.project-status');
        statusEl.className = `project-status ${newStatus}`;
        statusEl.innerHTML = `${this.getStatusIcon(newStatus)} ${this.capitalizeFirst(newStatus)}`;
        this.highlight(card);
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectCard;
}
