export default class ProjectCard {
    constructor(project) {
        this.project = project;
    }

    render() {
        const div = document.createElement('div');
        div.className = `project-card ${this.getStatusClass()}`;

        // Create header
        const header = document.createElement('div');
        header.className = 'project-header';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'project-name';
        nameSpan.textContent = this.project.name;

        const statusSpan = document.createElement('span');
        statusSpan.className = 'project-status';
        statusSpan.textContent = this.project.status;

        header.appendChild(nameSpan);
        header.appendChild(statusSpan);

        // Create details
        const details = document.createElement('div');
        details.className = 'project-details';

        // Health score
        const healthDiv = document.createElement('div');
        const healthLabel = document.createElement('span');
        healthLabel.textContent = 'Health Score: ';
        const healthValue = document.createElement('strong');
        healthValue.textContent = String(this.project.health_score);
        healthDiv.appendChild(healthLabel);
        healthDiv.appendChild(healthValue);

        // Last validated
        const lastValidatedDiv = document.createElement('div');
        const lastValidatedLabel = document.createElement('span');
        lastValidatedLabel.textContent = 'Last Validated: ';
        const lastValidatedValue = document.createElement('span');
        lastValidatedValue.textContent = this.formatDate(this.project.last_validated);
        lastValidatedDiv.appendChild(lastValidatedLabel);
        lastValidatedDiv.appendChild(lastValidatedValue);

        // Errors
        const errorsDiv = document.createElement('div');
        const errorsLabel = document.createElement('span');
        errorsLabel.textContent = 'Errors: ';
        const errorsValue = document.createElement('span');
        errorsValue.textContent = String(this.project.error_count);
        errorsDiv.appendChild(errorsLabel);
        errorsDiv.appendChild(errorsValue);

        details.appendChild(healthDiv);
        details.appendChild(lastValidatedDiv);
        details.appendChild(errorsDiv);

        div.appendChild(header);
        div.appendChild(details);

        return div;
    }

    getStatusClass() {
        if (this.project.status === 'error' || this.project.health_score < 50) {
            return 'error';
        } else if (this.project.status === 'warning' || this.project.health_score < 80) {
            return 'warning';
        }
        return 'success';
    }

    formatDate(timestamp) {
        if (!timestamp) return 'Never';
        return new Date(timestamp).toLocaleString();
    }
}
