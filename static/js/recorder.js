let mediaRecorder;
let recordedChunks = [];
let recordedBlob = null;

const startRecBtn = document.getElementById('startRecBtn');
const stopRecBtn = document.getElementById('stopRecBtn');
const recordingStatus = document.getElementById('recordingStatus');
const playbackAudio = document.getElementById('playbackAudio');

if(startRecBtn && stopRecBtn) {
  startRecBtn.addEventListener('click', async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      recordedChunks = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if(e.data.size > 0) {
          recordedChunks.push(e.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        recordedBlob = new Blob(recordedChunks, { type: 'audio/wav' });
        playbackAudio.src = URL.createObjectURL(recordedBlob);
        playbackAudio.style.display = 'block';
      };
      
      mediaRecorder.start();
      recordingStatus.innerText = 'Recording in progress...';
      startRecBtn.disabled = true;
      stopRecBtn.disabled = false;
    } catch (err) {
      console.error('Error accessing microphone', err);
      alert('Error accessing microphone: ' + err.message);
    }
  });

  stopRecBtn.addEventListener('click', () => {
    if(mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      recordingStatus.innerText = 'Recording stopped.';
      startRecBtn.disabled = false;
      stopRecBtn.disabled = true;
    }
  });
}
