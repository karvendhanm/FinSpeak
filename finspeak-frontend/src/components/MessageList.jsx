import { useEffect, useRef } from 'react';

function MessageList({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 bg-white bg-opacity-95 backdrop-blur-sm overflow-y-auto p-4 space-y-4 relative">
      {messages.length === 0 && (
        <div className="text-center mt-20">
          <div className="mb-8 flex justify-center">
            <div className="bg-gradient-to-br from-blue-600 to-green-600 p-6 rounded-full shadow-lg">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
              </svg>
            </div>
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-2">Grace Hopper Bank</h2>
          <p className="text-gray-500 text-lg mb-4">Voice Banking Assistant</p>
          <p className="text-gray-400">Press the microphone button to start</p>
        </div>
      )}
      
      {messages.length > 0 && (
        <div className="absolute top-4 left-4 flex items-center gap-2 opacity-30">
          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
          </svg>
          <span className="text-sm font-semibold text-blue-600">Grace Hopper Bank</span>
        </div>
      )}

      {messages.length > 0 && messages.map((msg, idx) => (
        <div
          key={idx}
          className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-md ${
              msg.type === 'user'
                ? 'bg-blue-600 text-white px-4 py-2 rounded-lg shadow-md'
                : msg.type === 'error'
                ? 'bg-red-100 text-red-700 px-4 py-2 rounded-lg'
                : 'bg-white text-gray-800 px-4 py-2 rounded-lg shadow-md border border-blue-100'
            }`}
          >
            <div className="whitespace-pre-line">{msg.text}</div>
            {msg.options && msg.options.length > 0 && (
              <div className="mt-3 space-y-2">
                {msg.options.map((option, optIdx) => (
                  <button
                    key={optIdx}
                    onClick={() => {
                      const event = new CustomEvent('optionSelected', { detail: option.display || option.id });
                      window.dispatchEvent(event);
                    }}
                    className="w-full text-left px-3 py-2 bg-white text-gray-800 rounded border border-gray-300 hover:bg-blue-50 hover:border-blue-400 transition-colors"
                  >
                    {option.text}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}

export default MessageList;
