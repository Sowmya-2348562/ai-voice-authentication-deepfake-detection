// Function to append command history (if needed)
function appendHistory(command, response) {
  const timestamp = new Date().toLocaleTimeString();
  const entry = `<p>[${timestamp}] <strong>Command:</strong> ${command}<br><strong>Response:</strong> ${response}</p>`;
  $("#historyOutput").prepend(entry);
}
function toggleInput(select) {
  const uploadInput = document.getElementById('uploadInput');
  if (select.value === 'live') {
      uploadInput.style.display = 'none';
  } else {
      uploadInput.style.display = 'block';
  }
}
// Handle text query form submission (for modals)
$('#textQueryForm').on('submit', function(e) {
e.preventDefault();
const formData = $(this).serialize();
$.post('/ask_text', formData, function(data) {
  if(data.response) {
    $('#textResponse').val(data.response);
  } else if(data.error) {
    $('#textResponse').val(data.error);
  }
});
});

// Handle audio form submission
$('#audioForm').on('submit', function(e) {
e.preventDefault();
const agentName = $('#audioAgentName').val();
const formData = new FormData();
formData.append('agent_name', agentName);
const audioFile = $('#audioFile')[0].files[0];
if(audioFile) {
  formData.append('audio', audioFile);
} else if (recordedBlob) {
  formData.append('audio', recordedBlob, 'recorded_audio.wav');
} else {
  alert("No audio file selected or recorded!");
  return;
}
$.ajax({
  url: '/upload_audio',
  type: 'POST',
  data: formData,
  contentType: false,
  processData: false,
  success: function(data) {
    if(data.transcription) {
      $('#transcriptionOutput').val(data.transcription);
    } else if(data.error) {
      $('#transcriptionOutput').val(data.error);
    }
  },
  error: function(err) {
    $('#transcriptionOutput').val('Error: ' + err.responseText);
  }
});
});
