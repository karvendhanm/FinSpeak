import { useState, useRef, useEffect } from 'react';
import VoiceRecorder from './VoiceRecorder';
import TextInput from './TextInput';
import MessageList from './MessageList';
import TypingIndicator from './TypingIndicator';
import { sendAudioToBackend, sendTextToBackend, verifyOTP } from '../utils/api';

const translations = {
  en: {
    title: "Nidhi",
    subtitle: "Voice Banking Assistant • Grace Hopper Bank",
    languageLabel: "Language:",
    noSpeech: "No speech detected. Please try again.",
    error: "Error:",
    invalidOTP: "Invalid OTP. Please try again."
  },
  hi: {
    title: "निधि",
    subtitle: "वॉयस बैंकिंग सहायक • ग्रेस हॉपर बैंक",
    languageLabel: "भाषा:",
    noSpeech: "कोई आवाज़ नहीं मिली। कृपया पुनः प्रयास करें।",
    error: "त्रुटि:",
    invalidOTP: "अमान्य OTP। कृपया पुनः प्रयास करें।"
  }
};

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [language, setLanguage] = useState('en');
  const audioRef = useRef(null);
  const languageRef = useRef(language);
  
  const t = translations[language];
  
  // Keep languageRef in sync with language state
  useEffect(() => {
    languageRef.current = language;
  }, [language]);

  // Handle option selection
  useEffect(() => {
    const handleOptionSelected = (event) => {
      console.log('📨 optionSelected event received:', event.detail, 'language:', languageRef.current);
      handleTextSubmit(event.detail, languageRef.current);
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
        transactions: response.transactions || null,
        payments: response.payments || null,
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
        text: t.invalidOTP
      }]);
    }
  };

  const handleAudioRecorded = async (transcript) => {
    // transcript is now a string from Web Speech API
    if (!transcript || transcript.trim() === '') {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: t.noSpeech
      }]);
      return;
    }
    
    // Show user message immediately
    setMessages(prev => [...prev, { type: 'user', text: transcript, timestamp: new Date() }]);
    setIsProcessing(true);

    try {
      const response = await sendTextToBackend(transcript, language);
      handleResponse(response);
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: t.error + ' ' + error.message 
      }]);
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = async (text, lang = language) => {
    console.log('📝 handleTextSubmit called with:', text, 'language:', lang);
    // Show user message immediately
    setMessages(prev => [...prev, { type: 'user', text: text, timestamp: new Date() }]);
    setIsProcessing(true);

    try {
      console.log('🚀 Sending to backend:', text, 'with language:', lang);
      const response = await sendTextToBackend(text, lang);
      console.log('✅ Backend response received:', response);
      handleResponse(response);
    } catch (error) {
      console.error('❌ Error in handleTextSubmit:', error);
      setMessages(prev => [...prev, { 
        type: 'error', 
        text: t.error + ' ' + error.message 
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
      
      
    <div className="flex flex-col h-[92vh] max-w-4xl w-full relative z-10">
      <header className="bg-gradient-to-r from-blue-700 to-blue-900 text-white p-5 rounded-t-xl shadow-2xl backdrop-blur-sm bg-opacity-95">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
              N
            </div>
            <div>
              <h1 className="text-2xl font-bold">{t.title}</h1>
              <p className="text-sm opacity-90">{t.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm opacity-90">{t.languageLabel}</span>
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-blue-800 text-white px-3 py-1 rounded-lg border border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
            </select>
          </div>
        </div>
      </header>

      <MessageList messages={messages} onOTPSubmit={handleOTPSubmit} language={language} />
      
      {isProcessing && <div className="px-4"><TypingIndicator /></div>}

      <div className="bg-white p-4 rounded-b-xl shadow-lg border-t border-gray-200 flex items-center gap-3">
        <VoiceRecorder 
          onAudioRecorded={handleAudioRecorded} 
          disabled={isProcessing}
          language={language}
        />
        <TextInput 
          onTextSubmit={handleTextSubmit}
          disabled={isProcessing}
          language={language}
        />
      </div>



      <audio ref={audioRef} className="hidden" />
    </div>
    </div>
  );
}

export default ChatInterface;
