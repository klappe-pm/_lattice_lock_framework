/**
 * Project Card Component
 * Displays project status with health indicator and actions
 * @namespace ProjectCard
 */

import { formatTime, escapeHtml } from '../utils.js';

export const ProjectCard = {
    /**
     * Creates a project card DOM element.
     * @param {Object} project - The project data.
     * @param {Object} callbacks - Callback functions for actions.
     * @param {Function} [callbacks.onValidate] - Handler for validate action.
     * @param {Function} [callbacks.onRollback] - Handler for rollback action.
     * @returns {HTMLElement} The project card element.
     */
    create(project, callbacks = {}) {
        const card = document.createElement('div');
        card.className = 'project-card';
        card.dataset.projectId = project.id;
        card.dataset.status = project.status;

        const statusIcon = this.getStatusIcon(project.status);
        const statusClass = project.status;

        card.innerHTML = `
            <div class="project-header">
                <span class="project-name">${escapeHtml(project.name)}</span>
                <span class="project-status ${escapeHtml(statusClass)}">
                    ${statusIcon}
                    ${escapeHtml(this.capitalizeFirst(project.status))}
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
                    <span>${formatTime(project.lastValidation)}</span>
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

    /**
     * Gets the SVG icon for a given status.
     * @param {string} status - The project status.
     * @returns {string} SVG string.
     */
    getStatusIcon(status) {
        const icons = {
            healthy: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
            warning: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
            error: '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>'
        };
        // Sanitize status to prevent injection if it's not one of the keys
        return icons[status] || icons.healthy;
    },

    /**
     * Capitalizes the first letter of a string.
     * @param {string} str - Input string.
     * @returns {string} Capitalized string.
     */
    capitalizeFirst(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Shows project details in an alert (for now).
     * @param {Object} project - Project object.
     */
    showDetails(project) {
        console.log('Showing details for project:', project);
        // Using alert for now as per original code, but could be improved
        alert(`Project: ${project.name}\nStatus: ${project.status}\nEntities: ${project.entities}\nConstraints: ${project.constraints}`);
    },

    /**
     * Temporarily highlights a project card.
     * @param {HTMLElement} card - The card element.
     */
    highlight(card) {
        card.classList.add('highlight');
        setTimeout(() => card.classList.remove('highlight'), 1000);
    },

    /**
     * Updates the status of a project card.
     * @param {HTMLElement} card - The card element.
     * @param {string} newStatus - The new status.
     */
    updateStatus(card, newStatus) {
        card.dataset.status = newStatus;
        const statusEl = card.querySelector('.project-status');
        if (statusEl) {
            statusEl.className = `project-status ${newStatus}`;
            statusEl.innerHTML = `${this.getStatusIcon(newStatus)} ${escapeHtml(this.capitalizeFirst(newStatus))}`;
        }
        this.highlight(card);
    }
};
