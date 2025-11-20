import { useState, useRef } from 'react';

function VoiceRecorder({ onAudioRecorded, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      console.log('Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('Microphone access granted');
      
      // Try different MIME types for better Mac compatibility
      let options = { mimeType: 'audio/webm;codecs=opus' };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'audio/webm' };
      }
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: 'audio/ogg;codecs=opus' };
      }
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = {};
      }
      
      console.log('Using MIME type:', options.mimeType || 'default');
      mediaRecorderRef.current = new MediaRecorder(stream, options);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        console.log('Audio chunk received:', e.data.size, 'bytes');
        chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        console.log('Recording stopped. Blob size:', audioBlob.size, 'bytes');
        onAudioRecorded(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start(100); // Collect data every 100ms
      console.log('Recording started');
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone error:', error);
      alert('Microphone error: ' + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-b-lg shadow-lg">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled}
        className={`w-full py-4 rounded-lg font-semibold transition ${
          isRecording 
            ? 'bg-red-500 hover:bg-red-600 text-white' 
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        } disabled:bg-gray-300 disabled:cursor-not-allowed`}
      >
        {isRecording ? '🔴 Stop Recording' : '🎤 Start Recording'}
      </button>
    </div>
  );
}

export default VoiceRecorder;
