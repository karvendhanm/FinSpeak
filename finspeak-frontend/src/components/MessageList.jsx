import { useEffect, useRef, useState } from 'react';

function MessageList({ messages, onOTPSubmit }) {
  const endRef = useRef(null);
  const [otpValues, setOtpValues] = useState(['', '', '', '', '', '']);
  const [isListening, setIsListening] = useState(false);
  const otpInputRefs = useRef([]);

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
          <p className="text-gray-500 text-lg mb-6">Voice Banking Assistant</p>
          
          <div className="max-w-md mx-auto bg-white rounded-xl shadow-lg p-6 border-2 border-blue-100">
            <div className="flex items-start gap-3 mb-4">
              <div className="bg-gradient-to-br from-blue-600 to-green-600 p-2 rounded-full mt-3">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-1">Namaste! I'm Nidhi</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Your voice banking assistant. I can help you with balance inquiries, fund transfers, transaction history, loans, credit cards, and payment reminders.
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-700 mb-2 font-medium text-center">Try saying:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li className="flex items-center justify-center gap-2">
                  <span className="text-blue-600">•</span>
                  "What's my balance?"
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="text-blue-600">•</span>
                  "Transfer money to Pratap Kumar"
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="text-blue-600">•</span>
                  "Show my loan status"
                </li>
                <li className="flex items-center justify-center gap-2">
                  <span className="text-blue-600">•</span>
                  "Any upcoming payments?"
                </li>
              </ul>
            </div>
            
            <p className="text-gray-400 text-sm text-center">Press the microphone button or type to start</p>
          </div>
        </div>
      )}
      


      {messages.length > 0 && messages.map((msg, idx) => {
        const formatTime = (date) => {
          if (!date) return '';
          return new Date(date).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        };
        
        return (
        <div
          key={idx}
          className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} gap-2 items-start`}
        >
          {msg.type !== 'user' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
              N
            </div>
          )}
          {msg.requiresOTP ? (
            <div className="max-w-md bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-400 rounded-2xl shadow-xl p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex-shrink-0 h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center shadow-lg">
                  <svg className="h-7 w-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-bold text-blue-900 mb-1">OTP Verification</h4>
                  <p className="text-gray-700 text-sm">{msg.text}</p>
                </div>
              </div>
              
              <div className="flex gap-2 justify-center mb-4">
                {otpValues.map((value, i) => (
                  <input
                    key={i}
                    ref={el => otpInputRefs.current[i] = el}
                    type="text"
                    maxLength="1"
                    value={value}
                    onChange={(e) => {
                      const val = e.target.value;
                      if (!/^[0-9]$/.test(val) && val !== '') return;
                      const newOtp = [...otpValues];
                      newOtp[i] = val;
                      setOtpValues(newOtp);
                      if (val && i < 5) otpInputRefs.current[i + 1]?.focus();
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Backspace' && !otpValues[i] && i > 0) {
                        otpInputRefs.current[i - 1]?.focus();
                      }
                    }}
                    className="w-12 h-12 text-center text-xl font-bold border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                  />
                ))}
              </div>
              
              <button
                onClick={() => {
                  if (isListening) {
                    setIsListening(false);
                  } else {
                    setIsListening(true);
                    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = 'en-IN';
                    recognition.onresult = (event) => {
                      const transcript = event.results[0][0].transcript;
                      const digits = transcript.replace(/\D/g, '').slice(0, 6);
                      const newOtp = digits.split('').concat(['', '', '', '', '', '']).slice(0, 6);
                      setOtpValues(newOtp);
                      setIsListening(false);
                    };
                    recognition.onerror = () => setIsListening(false);
                    recognition.start();
                  }
                }}
                className={`w-full px-4 py-2 mb-3 rounded-lg font-medium transition-all ${
                  isListening 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-blue-100 hover:bg-blue-200 text-blue-800'
                }`}
              >
                {isListening ? '🔴 Stop Listening' : '🎤 Speak OTP'}
              </button>
              
              <button
                onClick={() => {
                  const otp = otpValues.join('');
                  if (otp.length === 6) {
                    onOTPSubmit(otp);
                    setOtpValues(['', '', '', '', '', '']);
                  }
                }}
                disabled={otpValues.join('').length !== 6}
                className="w-full px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit OTP
              </button>
            </div>
          ) : msg.showSuccessModal ? (
            <div className="max-w-md bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-400 rounded-2xl shadow-xl p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 h-16 w-16 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg">
                  <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-bold text-green-800 mb-2 flex items-center gap-2">
                    Transfer Successful! {String.fromCodePoint(0x1F389)}
                  </h4>
                  <p className="text-gray-800 font-medium leading-relaxed">{msg.text}</p>
                </div>
              </div>
            </div>
          ) : (
            <div
              className={`max-w-md ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white px-4 py-2 rounded-lg shadow-md'
                  : msg.type === 'error'
                  ? 'bg-red-100 text-red-700 px-4 py-2 rounded-lg'
                  : (msg.text && msg.text.toLowerCase().includes('insufficient balance'))
                  ? 'bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-400 px-5 py-4 rounded-xl shadow-lg'
                  : 'bg-white text-gray-800 px-4 py-2 rounded-lg shadow-md border border-blue-100'
              }`}
            >
              {/* Always show text */}
              {(
                <div className="whitespace-pre-line">
                  {msg.text && msg.text.toLowerCase().includes('insufficient balance') ? (
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-red-500 flex items-center justify-center shadow-md">
                        <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <h4 className="text-base font-bold text-red-800 mb-1">Insufficient Balance</h4>
                        <p className="text-sm text-red-700 leading-relaxed">{msg.text.replace(/^insufficient balance[.:]/i, '').trim()}</p>
                      </div>
                    </div>
                  ) : (
                    msg.text || ''
                  )}
                </div>
              )}
              {msg.loans && msg.loans.length > 0 && (
                <div className="mt-3 space-y-3">
                  {msg.loans.map((loan, idx) => (
                    <div key={idx} className="p-4 rounded-lg bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-300 shadow-sm">
                      <div className="flex items-center gap-2 mb-3">
                        <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                        <h4 className="font-bold text-purple-900 text-base">{loan.type} Loan</h4>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Outstanding</div>
                          <div className="text-sm font-bold text-purple-900">₹{loan.outstanding}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">EMI</div>
                          <div className="text-sm font-bold text-purple-900">₹{loan.emi}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Due Date</div>
                          <div className="text-sm font-semibold text-gray-800">{loan.due_date}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Interest Rate</div>
                          <div className="text-sm font-semibold text-gray-800">{loan.interest_rate}%</div>
                        </div>
                      </div>
                      <div className="mt-2 bg-white bg-opacity-60 rounded-md p-2">
                        <div className="text-xs text-gray-600">Remaining Tenure</div>
                        <div className="text-sm font-semibold text-gray-800">{loan.tenure_remaining}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {msg.cards && msg.cards.length > 0 && (
                <div className="mt-3 space-y-3">
                  {msg.cards.map((card, idx) => (
                    <div key={idx} className="p-4 rounded-lg bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-300 shadow-sm">
                      <div className="flex items-center gap-2 mb-3">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                        <h4 className="font-bold text-blue-900 text-base">{card.name}</h4>
                        <span className="ml-auto text-xs font-mono text-gray-600">****{card.last_four}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Available Credit</div>
                          <div className="text-sm font-bold text-green-600">₹{card.available_credit}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Credit Limit</div>
                          <div className="text-sm font-bold text-blue-900">₹{card.credit_limit}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Total Due</div>
                          <div className="text-sm font-bold text-red-600">₹{card.total_due}</div>
                        </div>
                        <div className="bg-white bg-opacity-60 rounded-md p-2">
                          <div className="text-xs text-gray-600">Minimum Due</div>
                          <div className="text-sm font-semibold text-orange-600">₹{card.minimum_due}</div>
                        </div>
                      </div>
                      <div className="mt-2 bg-white bg-opacity-60 rounded-md p-2">
                        <div className="text-xs text-gray-600">Payment Due On</div>
                        <div className="text-sm font-semibold text-gray-800">{card.due_date}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {msg.payments && msg.payments.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.payments.map((payment, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-gradient-to-r from-orange-50 to-yellow-50 border-l-4 border-orange-400">
                      <div className="flex justify-between items-start gap-3">
                        <div className="flex-1">
                          <div className="font-semibold text-gray-900 text-sm">{payment.type}</div>
                          <div className="text-xs text-gray-600 mt-1">
                            Due on {payment.due_date}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-base font-bold text-orange-600">₹{payment.amount}</div>
                          <div className={`text-xs font-medium mt-1 ${
                            payment.days_left <= 3 ? 'text-red-600' : payment.days_left <= 7 ? 'text-orange-600' : 'text-gray-600'
                          }`}>
                            {payment.days_left} {payment.days_left === 1 ? 'day' : 'days'} left
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {msg.transactions && msg.transactions.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  {msg.transactions.map((txn, idx) => (
                    <div key={idx} className={`p-2 rounded-md border-l-3 transition-all hover:shadow-sm ${
                      txn.type === 'credit' 
                        ? 'bg-green-50 border-green-500 hover:bg-green-100' 
                        : 'bg-red-50 border-red-500 hover:bg-red-100'
                    }`}>
                      <div className="flex justify-between items-start gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-gray-900 text-xs">{txn.description}</div>
                          <div className="text-[10px] text-gray-500 mt-0.5">{txn.date}</div>
                        </div>
                        <div className={`text-sm font-bold whitespace-nowrap ${
                          txn.type === 'credit' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {txn.type === 'credit' ? '+' : '-'}₹{txn.amount}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {msg.confirmation && msg.confirmation.amount && (
                <div className="mt-3">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600 text-sm">Amount:</span>
                      <span className="font-semibold text-gray-800">₹{msg.confirmation.amount || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 text-sm">From:</span>
                      <span className="font-semibold text-gray-800">{msg.confirmation.from_account || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 text-sm">To:</span>
                      <span className="font-semibold text-gray-800">{msg.confirmation.to_beneficiary || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 text-sm">Mode:</span>
                      <span className="font-semibold text-gray-800">{msg.confirmation.mode || 'N/A'}</span>
                    </div>
                  </div>
                  {msg.confirmation.needs_confirmation && (
                    <div className="mt-3 flex gap-3">
                      <button
                        onClick={() => {
                          console.log('✅ Yes button clicked - dispatching event');
                          const event = new CustomEvent('optionSelected', { detail: 'Yes confirm' });
                          window.dispatchEvent(event);
                        }}
                        className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg"
                      >
                        ✓ Yes, Confirm
                      </button>
                      <button
                        onClick={() => {
                          console.log('❌ No button clicked - dispatching event');
                          const event = new CustomEvent('optionSelected', { detail: 'No' });
                          window.dispatchEvent(event);
                        }}
                        className="flex-1 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-lg hover:from-red-600 hover:to-red-700 transition-all shadow-md hover:shadow-lg"
                      >
                        ✕ No, Cancel
                      </button>
                    </div>
                  )}
                </div>
              )}
              {msg.options && msg.options.length > 0 && (
                <div className="mt-3 space-y-2">
                  {msg.options.map((option, optIdx) => {
                    const isIMPS = option.text.includes('IMPS');
                    const isNEFT = option.text.includes('NEFT');
                    const isRTGS = option.text.includes('RTGS');
                    const isTransferMode = isIMPS || isNEFT || isRTGS;
                    
                    return (
                      <button
                        key={optIdx}
                        onClick={() => {
                          const event = new CustomEvent('optionSelected', { detail: option.text });
                          window.dispatchEvent(event);
                        }}
                        className="w-full text-left px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 text-gray-800 rounded-lg border-l-4 border-blue-400 hover:from-blue-100 hover:to-indigo-100 hover:shadow-md hover:scale-[1.02] transition-all duration-200 flex items-center gap-3"
                      >
                        {isIMPS ? (
                          <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        ) : isNEFT ? (
                          <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : isRTGS ? (
                          <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        )}
                        <span className="font-medium">{option.text}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          )}
          {msg.type === 'user' && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
              U
            </div>
          )}
          {msg.timestamp && (
            <div className="flex-shrink-0 text-xs text-gray-400 mt-2">
              {formatTime(msg.timestamp)}
            </div>
          )}
        </div>
        );
      })}
      <div ref={endRef} />
    </div>
  );
}

export default MessageList;
