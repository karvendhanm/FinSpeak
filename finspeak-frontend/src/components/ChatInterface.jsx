import { useState, useRef } from 'react';
import VoiceRecorder from './VoiceRecorder';
import TextInput from './TextInput';
import MessageList from './MessageList';
import OTPModal from './OTPModal';
import TypingIndicator from './TypingIndicator';
import { sendAudioToBackend, sendTextToBackend, verifyOTP } from '../utils/api';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const audioRef = useRef(null);

  const handleResponse = (response) => {
    // Remove typing indicator
    setIsProcessing(false);
    
    if (response.text) {
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        text: response.text,
        audio: response.audioUrl 
      }]);

      if (response.audioUrl && audioRef.current) {
        audioRef.current.src = response.audioUrl;
        audioRef.current.play();
      }
    }
    
    // Check if OTP is required
    if (response.requiresOTP) {
      setCurrentSessionId(response.sessionId);
      setShowOTPModal(true);
    }
  };

  const handleOTPSubmit = async (otp) => {
    try {
      const response = await verifyOTP(otp, currentSessionId);
      
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        text: response.text,
        audio: response.audioUrl 
      }]);

      if (response.audioUrl && audioRef.current) {
        audioRef.current.src = response.audioUrl;
        audioRef.current.play();
      }
      
      setShowOTPModal(false);
      setCurrentSessionId(null);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: 'Invalid OTP. Please try again.' 
      }]);
    }
  };

  const handleAudioRecorded = async (audioBlob) => {
    setIsProcessing(true);

    try {
      // Step 1: Transcribe audio
      const transcribeResponse = await sendAudioToBackend(audioBlob);
      
      // Check if transcription was successful
      if (!transcribeResponse.userText || transcribeResponse.userText.trim() === '') {
        // No speech detected or empty transcription
        if (transcribeResponse.text) {
          // Backend returned error message
          handleResponse(transcribeResponse);
        } else {
          // Unexpected empty response
          setMessages(prev => [...prev, { 
            type: 'error', 
            text: 'No speech detected. Please try again.' 
          }]);
          setIsProcessing(false);
        }
        return;
      }
      
      // Show user message immediately after transcription
      setMessages(prev => [...prev, { type: 'user', text: transcribeResponse.userText }]);
      
      // Step 2: Process with LLM (same as text input)
      const llmResponse = await sendTextToBackend(transcribeResponse.userText);
      handleResponse(llmResponse);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: 'Error: ' + error.message 
      }]);
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = async (text) => {
    // Show user message immediately
    setMessages(prev => [...prev, { type: 'user', text: text }]);
    setIsProcessing(true);

    try {
      const response = await sendTextToBackend(text);
      handleResponse(response);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: 'Error: ' + error.message 
      }]);
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      <header className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h1 className="text-2xl font-bold">FinSpeak</h1>
        <p className="text-sm">Voice Banking Assistant</p>
      </header>

      <MessageList messages={messages} />
      
      {isProcessing && <div className="px-4"><TypingIndicator /></div>}

      <VoiceRecorder 
        onAudioRecorded={handleAudioRecorded} 
        disabled={isProcessing}
      />

      <TextInput 
        onTextSubmit={handleTextSubmit}
        disabled={isProcessing}
      />

      {showOTPModal && (
        <OTPModal 
          onSubmit={handleOTPSubmit}
          onClose={() => setShowOTPModal(false)}
        />
      )}

      <audio ref={audioRef} className="hidden" />
    </div>
  );
}

export default ChatInterface;
