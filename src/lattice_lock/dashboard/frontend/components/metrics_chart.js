/**
 * Metrics Chart Component
 * Chart.js visualizations for dashboard metrics
 */

const MetricsChart = {
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
                        display: false
                    }
                },
                cutout: '60%'
            }
        });
    },

    createBar(canvasId, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Usage',
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

    updateDoughnut(chart, data) {
        if (!chart || !data) return;

        chart.data.datasets[0].data = [
            data.passed || 0,
            data.failed || 0,
            data.warnings || 0
        ];
        chart.update('none');
    },

    updateBar(chart, data) {
        if (!chart || !data) return;

        const labels = Object.keys(data);
        const values = Object.values(data);

        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = this.colors.background.slice(0, labels.length);
        chart.update('none');
    },

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

    destroy(chart) {
        if (chart) {
            chart.destroy();
        }
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = MetricsChart;
}
