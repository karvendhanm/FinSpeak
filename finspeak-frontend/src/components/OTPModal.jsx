import { useState } from 'react';

function OTPModal({ onSubmit, onClose }) {
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (otp.length === 6) {
      onSubmit(otp);
      setOtp('');
      setError('');
    } else {
      setError('Please enter a 6-digit OTP');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Enter OTP</h2>
        <p className="text-gray-600 mb-4">Please enter the 6-digit OTP to complete this transaction</p>
        
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            maxLength="6"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-2xl tracking-widest mb-2"
            autoFocus
          />
          
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={otp.length !== 6}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default OTPModal;
