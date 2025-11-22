function TypingIndicator() {
  return (
    <div className="flex justify-start gap-2 items-center">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
        N
      </div>
      <div className="bg-gray-200 px-4 py-3 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="text-gray-600 text-sm">Nidhi is thinking</span>
          <div className="flex space-x-1">
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TypingIndicator;
