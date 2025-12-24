/**
 * Metrics Chart Component
 * Chart.js visualizations for dashboard metrics
 * @namespace MetricsChart
 */
export const MetricsChart = {
    /**
     * Color palette for charts.
     */
    colors: {
        primary: '#3b82f6',
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
        secondary: '#64748b',
        background: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(100, 116, 139, 0.8)',
            'rgba(168, 85, 247, 0.8)',
            'rgba(236, 72, 153, 0.8)',
            'rgba(20, 184, 166, 0.8)'
        ]
    },

    /**
     * Creates a doughnut chart instance.
     * @param {string} canvasId - The ID of the canvas element.
     * @param {string} title - Chart title.
     * @returns {Chart|null} The Chart.js instance or null if canvas not found.
     */
    createDoughnut(canvasId, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed', 'Warnings'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.error,
                        this.colors.warning
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    title: {
                        display: !!title,
                        text: title
                    }
                },
                cutout: '60%'
            }
        });
    },

    /**
     * Creates a bar chart instance.
     * @param {string} canvasId - The ID of the canvas element.
     * @param {string} title - Chart title.
     * @returns {Chart|null} The Chart.js instance or null if canvas not found.
     */
    createBar(canvasId, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: title || 'Usage',
                    data: [],
                    backgroundColor: this.colors.background,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: !!title,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    },

    /**
     * Creates a line chart instance.
     * @param {string} canvasId - The ID of the canvas element.
     * @param {string} title - Chart title.
     * @returns {Chart|null} The Chart.js instance or null if canvas not found.
     */
    createLine(canvasId, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: title,
                    data: [],
                    borderColor: this.colors.primary,
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: !!title,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    },

    /**
     * Updates a doughnut chart with new data.
     * @param {Chart} chart - The Chart.js instance.
     * @param {Object} data - Data object containing passed, failed, warnings counts.
     */
    updateDoughnut(chart, data) {
        if (!chart || !data) return;

        chart.data.datasets[0].data = [
            data.passed || 0,
            data.failed || 0,
            data.warnings || 0
        ];
        chart.update('none');
    },

    /**
     * Updates a bar chart with new data.
     * @param {Chart} chart - The Chart.js instance.
     * @param {Object} data - Object where keys are labels and values are data points.
     */
    updateBar(chart, data) {
        if (!chart || !data || typeof data !== 'object') return;

        const labels = Object.keys(data);
        const values = Object.values(data).map(v => Number(v) || 0);

        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = this.colors.background.slice(0, labels.length);
        chart.update('none');
    },

    /**
     * Updates a line chart with new data.
     * @param {Chart} chart - The Chart.js instance.
     * @param {Array<number>} data - Array of data points.
     * @param {string} [label] - Optional new label for the dataset.
     */
    updateLine(chart, data, label) {
        if (!chart || !data) return;

        const labels = data.map((_, i) => {
            const date = new Date();
            date.setHours(date.getHours() - (data.length - i - 1));
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });

        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        if (label) {
            chart.data.datasets[0].label = label;
        }
        chart.update('none');
    },

    /**
     * Destroys a chart instance.
     * @param {Chart} chart - The chart to destroy.
     */
    destroy(chart) {
        if (chart) {
            chart.destroy();
        }
    }
};
