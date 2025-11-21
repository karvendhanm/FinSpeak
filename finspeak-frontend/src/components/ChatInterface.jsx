import { useState, useRef, useEffect } from 'react';
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

  // Handle option selection
  useEffect(() => {
    const handleOptionSelected = (event) => {
      handleTextSubmit(event.detail);
    };
    window.addEventListener('optionSelected', handleOptionSelected);
    return () => window.removeEventListener('optionSelected', handleOptionSelected);
  }, []);

  const handleResponse = (response) => {
    // Remove typing indicator
    setIsProcessing(false);
    
    // Add confirmation message first if present
    if (response.confirmation) {
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        text: response.confirmation
      }]);
    }
    
    if (response.text) {
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        text: response.text,
        audio: response.audioUrl,
        options: response.options || null
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

  const handleAudioRecorded = async (transcript) => {
    // transcript is now a string from Web Speech API
    if (!transcript || transcript.trim() === '') {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: 'No speech detected. Please try again.' 
      }]);
      return;
    }
    
    // Show user message immediately
    setMessages(prev => [...prev, { type: 'user', text: transcript }]);
    setIsProcessing(true);

    try {
      const response = await sendTextToBackend(transcript);
      handleResponse(response);
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 p-8 flex items-center justify-center relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20">
          <svg className="w-64 h-64 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>
        </div>
        <div className="absolute bottom-20 right-20">
          <svg className="w-64 h-64 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>
        </div>
      </div>
      
      {/* Bank Name Watermark */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="text-center transform -rotate-12">
          <h1 className="text-9xl font-bold text-white opacity-10 tracking-wider">GRACE HOPPER</h1>
          <p className="text-5xl font-light text-white opacity-10 tracking-widest mt-4">BANK</p>
        </div>
      </div>
      
    <div className="flex flex-col h-[85vh] max-w-4xl w-full relative z-10">
      <header className="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-5 rounded-t-xl shadow-2xl backdrop-blur-sm bg-opacity-95">
        <div className="flex items-center gap-3">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>
          <div>
            <h1 className="text-2xl font-bold">FinSpeak</h1>
            <p className="text-sm opacity-90">Grace Hopper Bank</p>
          </div>
        </div>
      </header>

      <MessageList messages={messages} />
      
      {isProcessing && <div className="px-4"><TypingIndicator /></div>}

      <div className="bg-white p-4 rounded-b-xl shadow-lg border-t border-gray-200 flex items-center gap-3">
        <VoiceRecorder 
          onAudioRecorded={handleAudioRecorded} 
          disabled={isProcessing}
        />
        <TextInput 
          onTextSubmit={handleTextSubmit}
          disabled={isProcessing}
        />
      </div>

      {showOTPModal && (
        <OTPModal 
          onSubmit={handleOTPSubmit}
          onClose={() => setShowOTPModal(false)}
        />
      )}

      <audio ref={audioRef} className="hidden" />
    </div>
    </div>
  );
}

export default ChatInterface;
