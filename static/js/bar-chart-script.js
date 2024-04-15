document.getElementById('chart-bar').addEventListener('htmx:afterRequest', function(event) {
    // Process the JSON response here
    const responseData = event.detail.xhr.response;
    const jsonData = JSON.parse(responseData);
    const labels = jsonData['labels']
    const data = jsonData['data']

    const dataBar = {
        labels: labels,
        datasets: [
          {
            label: "Amount",
            data: data,
            backgroundColor: 'rgb(139,44,255)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          },
        ],
      };
    updateBarChart(dataBar)
});

function updateBarChart(dataBar) {
  
    var ctx = document.getElementById('chartBar');

    var existingChart = Chart.getChart('chartBar');
    if (existingChart) {
        // If the chart exists, destroy it
        existingChart.destroy();
    }
  
    var chartBar = new Chart(ctx, {
        type: "bar",
        data: dataBar,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
  }