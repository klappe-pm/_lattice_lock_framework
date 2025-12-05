export default class ProjectCard {
    constructor(project) {
        this.project = project;
    }

    render() {
        const div = document.createElement('div');
        div.className = `project-card ${this.getStatusClass()}`;

        div.innerHTML = `
            <div class="project-header">
                <span class="project-name">${this.project.name}</span>
                <span class="project-status">${this.project.status}</span>
            </div>
            <div class="project-details">
                <div>Health Score: <strong>${this.project.health_score}</strong></div>
                <div>Last Validated: ${this.formatDate(this.project.last_validated)}</div>
                <div>Errors: ${this.project.error_count}</div>
            </div>
        `;

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
