# FinSpeak – Frontend (Web UI)

FinSpeak is a voice-driven conversational banking assistant.  
This repository contains a lightweight, React-based web interface that communicates with a Python FastAPI backend.

The purpose of the frontend is to:
- Capture voice input through the user’s microphone
- Send recorded audio to the backend for ASR → LLM → Banking-API routing
- Display assistant responses in a chat-like interface
- Present an OTP input modal when backend requires OTP verification
- Play text-to-speech audio returned by the backend

This UI is intentionally minimal to support rapid iteration and hackathon prototyping.



