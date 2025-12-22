export default class MetricsChart {
    constructor(canvasElement) {
        this.ctx = canvasElement.getContext('2d');
        this.chart = null;
        this.initChart();
    }

    initChart() {
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Success Rate',
                        data: [],
                        borderColor: '#2ecc71',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Error Rate',
                        data: [],
                        borderColor: '#e74c3c',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                animation: {
                    duration: 0 // Disable animation for real-time updates performance
                }
            }
        });
    }

    update(metricsData) {
        // Assuming metricsData is an array of time-series points
        // or a single point to append.
        // For simplicity, let's assume we receive the full recent history or update the last point.

        if (metricsData.labels && metricsData.datasets) {
            // Full update
            this.chart.data = metricsData;
        } else if (metricsData.timestamp) {
            // Incremental update
            this.chart.data.labels.push(new Date(metricsData.timestamp).toLocaleTimeString());
            this.chart.data.datasets[0].data.push(metricsData.success_rate);
            this.chart.data.datasets[1].data.push(metricsData.error_rate);

            // Keep only last 20 points
            if (this.chart.data.labels.length > 20) {
                this.chart.data.labels.shift();
                this.chart.data.datasets.forEach(dataset => dataset.data.shift());
            }
        }

        this.chart.update();
    }
}
