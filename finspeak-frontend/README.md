# FinSpeak Frontend

Voice-driven conversational banking assistant UI.

## Setup

```bash
npm install
npm run dev
```

## Environment Variables

Create a `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── ChatInterface.jsx    # Main chat container
│   ├── VoiceRecorder.jsx     # Audio recording
│   ├── MessageList.jsx       # Chat messages display
│   └── OTPModal.jsx          # OTP verification modal
├── utils/
│   └── api.js                # Backend API calls
├── App.jsx                   # Root component
└── index.css                 # Tailwind styles
```

## Backend Integration

Expected backend endpoints:
- `POST /api/voice` - Send audio file, receive text + audio response
- `POST /api/verify-otp` - Submit OTP for verification

Expected response format:
```json
{
  "userText": "Transcribed user speech",
  "text": "Assistant response text",
  "audioUrl": "base64 or URL to TTS audio",
  "requiresOTP": false,
  "sessionId": "optional-session-id"
}
```
