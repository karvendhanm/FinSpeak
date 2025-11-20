import { useEffect, useRef } from 'react';

function MessageList({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 bg-white overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-20">
          <p className="text-lg">👋 Welcome to FinSpeak</p>
          <p className="text-sm">Press the microphone button to start</p>
        </div>
      )}

      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-xs px-4 py-2 rounded-lg ${
              msg.type === 'user'
                ? 'bg-blue-500 text-white'
                : msg.type === 'error'
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-200 text-gray-800'
            }`}
          >
            {msg.text}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

export default MessageList;
