import { useState, useRef, useEffect } from 'react';
import VoiceRecorder from './VoiceRecorder';
import TextInput from './TextInput';
import MessageList from './MessageList';
import TypingIndicator from './TypingIndicator';
import { sendAudioToBackend, sendTextToBackend, verifyOTP } from '../utils/api';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
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
    
    if (response.text) {
      setMessages(prev => [...prev, { 
        type: 'assistant', 
        text: response.text,
        audio: response.audioUrl,
        options: response.options || null,
        confirmation: response.confirmation || null,
        requiresOTP: response.requiresOTP || false,
        sessionId: response.sessionId || null,
        timestamp: new Date()
      }]);

      if (response.audioUrl && audioRef.current) {
        audioRef.current.src = response.audioUrl;
        audioRef.current.play();
      }
    }
    
    // Store session ID for OTP verification
    if (response.requiresOTP) {
      setCurrentSessionId(response.sessionId);
    }
  };

  const handleOTPSubmit = async (otp) => {
    try {
      const response = await verifyOTP(otp, currentSessionId);
      
      // Remove OTP message and add success message
      setMessages(prev => {
        const filtered = prev.filter(m => !m.requiresOTP);
        return [...filtered, { 
          type: 'assistant', 
          text: response.text,
          audio: response.audioUrl,
          showSuccessModal: response.showSuccessModal || false,
          timestamp: new Date()
        }];
      });

      if (response.audioUrl && audioRef.current) {
        audioRef.current.src = response.audioUrl;
        audioRef.current.play();
      }
      
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
    setMessages(prev => [...prev, { type: 'user', text: transcript, timestamp: new Date() }]);
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
    setMessages(prev => [...prev, { type: 'user', text: text, timestamp: new Date() }]);
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
      
      
    <div className="flex flex-col h-[85vh] max-w-4xl w-full relative z-10">
      <header className="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-5 rounded-t-xl shadow-2xl backdrop-blur-sm bg-opacity-95">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
            N
          </div>
          <div>
            <h1 className="text-2xl font-bold">Nidhi</h1>
            <p className="text-sm opacity-90">Voice Banking Assistant • Grace Hopper Bank</p>
          </div>
        </div>
      </header>

      <MessageList messages={messages} onOTPSubmit={handleOTPSubmit} />
      
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



      <audio ref={audioRef} className="hidden" />
    </div>
    </div>
  );
}

export default ChatInterface;
