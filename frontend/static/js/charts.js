
document.addEventListener('DOMContentLoaded', () => {

    if (typeof Chart === 'undefined') return;

    initLineChart();
    initPieChart();

});

/* ===== LINE CHART (THIS YEAR) ===== */
function initLineChart() {

    const ctx = document.getElementById('lineChart');
    if (!ctx) return;

    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Sessions',
                    data: {{ monthly_sessions | tojson }},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Documents',
                    data: {{ monthly_docs | tojson }},
                    borderColor: '#1cc88a',
                    backgroundColor: 'rgba(28, 200, 138, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Users',
                    data: {{ monthly_users | tojson }},
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
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            label += context.parsed.y;
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Sessions / Documents'
                    },
                    ticks: {
                        precision: 0
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Users'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}


/* ===== PIE CHART (MONTHLY REPORT) ===== */
function initPieChart() {

    const ctx = document.getElementById('pieChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Hoàn thành', 'Chưa hoàn thành'],
            datasets: [{
                data: [{{ completed }}, {{ uncompleted }}],
                backgroundColor: [
                    '#1cc88a',
                    '#e74a3b'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
