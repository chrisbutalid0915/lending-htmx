document.getElementById('chartDoughnut').addEventListener('htmx:afterRequest', function(event) {
  // Process the JSON response here
  const responseData = event.detail.xhr.response;
  const jsonData = JSON.parse(responseData);
  const labels = jsonData['labels']
  const data = jsonData['data']

  const dataDoughnut = {
    labels: labels,
    datasets: [
      {
        label: "Amount",
        data: data,
        backgroundColor: [
          "rgb(133, 105, 241)",
          "rgb(164, 101, 241)",
          "rgb(101, 143, 241)",
        ],
        hoverOffset: 4,
      },
    ],
  };

  updateChart(dataDoughnut)
});

function updateChart(dataDoughnut) {
  var ctx = document.getElementById('chartDoughnut');
  var chartBar = new Chart(ctx, {
      type: "doughnut",
      data: dataDoughnut,
      options: {
      }
  });
}