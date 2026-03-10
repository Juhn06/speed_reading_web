/**
 * Charts
 * Vẽ biểu đồ thống kê
 */

// Initialize chart when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chartCanvas = document.getElementById('progressChart');

    if (chartCanvas && typeof Chart !== 'undefined') {
        initProgressChart();
    }
});

// Initialize progress chart
async function initProgressChart() {
    try {
        const data = await API.getStats();

        const ctx = document.getElementById('progressChart').getContext('2d');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Số phiên đọc',
                        data: data.sessions,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Số từ đã đọc',
                        data: data.words,
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += formatNumber(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Số phiên đọc'
                        },
                        ticks: {
                            precision: 0
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Số từ'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            callback: function(value) {
                                return formatNumber(value);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}