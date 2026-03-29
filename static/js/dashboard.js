// Connect to Socket.IO
const socket = io();  // By default, connects to the same host/port

// When performance stats are received, update the UI
socket.on('perf_stats', data => {
  const cpuBar = document.getElementById('cpuUsageBar');
  const memBar = document.getElementById('memUsageBar');
  if (cpuBar) {
    cpuBar.style.width = data.cpu + '%';
    cpuBar.textContent = data.cpu + '%';
  }
  if (memBar) {
    memBar.style.width = data.mem + '%';
    memBar.textContent = data.mem + '%';
  }
});

// When a new log entry comes in
socket.on('new_log', log => {
  const logList = document.getElementById('logList');
  const entry = document.createElement('tr');
  entry.innerHTML = `<td>${log.timestamp}</td><td>${log.user}</td><td>${log.event}</td><td>${log.info}</td>`;
  if (logList) {
    logList.prepend(entry);
  }
  // Update the authPieChart if it exists
  if (window.authPieChart) {
    if (log.info.includes('SUCCESS')) {
      window.authPieChart.data.datasets[0].data[0] += 1;
    } else {
      window.authPieChart.data.datasets[0].data[1] += 1;
    }
    window.authPieChart.update();
  }
});

// When an alert is received (e.g., suspicious deepfake)
socket.on('alert', alertData => {
  showAlert(alertData.msg);
});

// Function to show alerts to user
function showAlert(message) {
  const alertBox = document.getElementById('alertBox');
  if (alertBox) {
    alertBox.textContent = message;
    alertBox.style.display = 'block';
    alertBox.classList.add('show');
    // Remove after 10 seconds
    setTimeout(() => {
      alertBox.classList.remove('show');
      alertBox.style.display = 'none';
    }, 10000);
  } else {
    alert(message);
  }
}
