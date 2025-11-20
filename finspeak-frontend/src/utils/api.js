import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const sendAudioToBackend = async (audioBlob) => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await axios.post(`${API_BASE_URL}/api/voice`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });

  return response.data;
};

export const sendTextToBackend = async (text) => {
  const response = await axios.post(`${API_BASE_URL}/api/text`, null, {
    params: { text }
  });

  return response.data;
};

export const verifyOTP = async (otp, sessionId) => {
  const response = await axios.post(`${API_BASE_URL}/api/verify-otp`, null, {
    params: { otp, sessionId }
  });

  return response.data;
};


