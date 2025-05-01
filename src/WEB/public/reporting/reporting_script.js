document.addEventListener('DOMContentLoaded', function() {
  const ReportingData = fetch('/ReportingData')

  const ctx = document.getElementById('salesChart').getContext('2d');
  const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [{
          label: 'Sales',
          data: [10, 25, 14],
          backgroundColor: ['#4bc0c0', '#ff6384', '#36a2eb']
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    })
});