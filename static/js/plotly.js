
<script src="https://cdn.plot.ly/plotly-latest.min.js">
  const heatmapData = {
    z: {{ anomaly_matrix|tojson }},  
    type: 'heatmap',
    colorscale: 'Viridis'
  };
  const layout = {
    title: 'Anomaly Pattern Heatmap',
    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
    font: { color: getComputedStyle(document.body).getPropertyValue('--text-color') }
  };
  Plotly.newPlot('anomalyHeatmap', [heatmapData], layout);
</script>
