# FinSpeak Backend

FastAPI backend with AWS Transcribe integration.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your AWS credentials:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. Create an S3 bucket in AWS Console for audio storage

4. Update `.env` with your bucket name

## Run

```bash
python server.py
```

Server runs on http://localhost:8000

## How it works

1. Receives audio from frontend
2. Uploads audio to S3
3. Starts AWS Transcribe job
4. Waits for transcription
5. Returns transcribed text
6. Cleans up S3 and transcription job
