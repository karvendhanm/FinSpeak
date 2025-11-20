from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3
import uuid
import os
import time
import subprocess
import tempfile
import random
from llm_module import process_user_input
from config import (
    S3_BUCKET_NAME,
    MASTER_OTP,
    OTP_REQUIRED_FUNCTIONS,
    POLLY_VOICE_ID,
    POLLY_ENGINE,
    TRANSCRIBE_LANGUAGE_CODE,
    TRANSCRIBE_SAMPLE_RATE
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')
polly_client = boto3.client('polly')

# In-memory session storage for OTP
pending_sessions = {}

def execute_function(function_name, params):
    """Execute banking functions and return response text"""
    if function_name == "transfer_money":
        return "Transfer completed successfully! [Dummy: Would execute transfer_money]"
    elif function_name == "get_balance":
        return "Your current account balance is $12,450.75. [Dummy response]"
    elif function_name == "get_transactions":
        return "Here are your recent transactions: [Dummy: Would show transaction list]"
    elif function_name == "greet":
        return "Hello! I'm your banking assistant. How can I help you today?"
    elif function_name == "general_query":
        return f"I received your message: '{params.get('text', '')}'. How can I assist you with your banking needs?"
    else:
        return "I can help you with that. [Dummy response]"

def text_to_speech(text):
    """Convert text to speech using AWS Polly and return base64 audio"""
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=POLLY_VOICE_ID,
        Engine=POLLY_ENGINE
    )
    
    audio_data = response['AudioStream'].read()
    import base64
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    return f"data:audio/mp3;base64,{audio_base64}"

@app.post("/api/verify-otp")
async def verify_otp(otp: str, sessionId: str):
    print(f"Verifying OTP: {otp} for session: {sessionId}")
    
    # Check if session exists
    if sessionId not in pending_sessions:
        return JSONResponse({"error": "Invalid or expired session"}, status_code=400)
    
    session = pending_sessions[sessionId]
    
    # Validate OTP (accept generated OTP or master OTP)
    if otp == session["otp"] or otp == MASTER_OTP:
        print(f"✅ OTP verified! Executing {session['function']}")
        
        # Execute the pending function
        function_name = session["function"]
        params = session["params"]
        
        response_text = execute_function(function_name, params)
        
        # Clean up session
        del pending_sessions[sessionId]
        
        # Convert to speech
        audio_url = text_to_speech(response_text)
        
        return JSONResponse({
            "text": response_text,
            "audioUrl": audio_url
        })
    else:
        print(f"❌ Invalid OTP")
        return JSONResponse({"error": "Invalid OTP. Please try again."}, status_code=400)

@app.post("/api/text")
async def process_text(text: str):
    print(f"Received text: {text}")
    
    # Step 1: LLM identifies intent and function
    llm_result = process_user_input(text)
    print(f"LLM identified function: {llm_result['function']}")
    
    function_name = llm_result["function"]
    params = llm_result["params"]
    
    # Step 2: Backend deterministically checks if OTP is required
    requires_otp = function_name in OTP_REQUIRED_FUNCTIONS
    print(f"OTP required: {requires_otp} (Backend security check)")
    
    if requires_otp:
        # Generate OTP and create session
        session_id = str(uuid.uuid4())
        otp = str(random.randint(100000, 999999))
        
        pending_sessions[session_id] = {
            "function": function_name,
            "params": params,
            "otp": otp,
            "timestamp": time.time()
        }
        
        print(f"\n🔐 OTP for session {session_id}: {otp}")
        print(f"   (Or use master OTP: {MASTER_OTP})\n")
        
        response_text = "For security, please enter the OTP sent to your registered device to complete this transaction."
        audio_url = text_to_speech(response_text)
        
        return JSONResponse({
            "userText": text,
            "text": response_text,
            "audioUrl": audio_url,
            "requiresOTP": True,
            "sessionId": session_id
        })
    
    # No OTP required - execute function directly
    response_text = execute_function(function_name, params)
    audio_url = text_to_speech(response_text)
    
    return JSONResponse({
        "userText": text,
        "text": response_text,
        "audioUrl": audio_url
    })

@app.post("/api/voice")
async def process_voice(audio: UploadFile = File(...)):
    start_time = time.time()
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        s3_key = f"audio/{file_id}.webm"
        
        # Save and convert audio
        audio_content = await audio.read()
        print(f"Received audio file: {len(audio_content)} bytes")
        t1 = time.time()
        print(f"⏱️  Audio received: {t1 - start_time:.2f}s")
        
        # Save webm to temp file
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
            temp_webm.write(audio_content)
            temp_webm_path = temp_webm.name
        
        # Convert to WAV using ffmpeg (optimized)
        temp_wav_path = temp_webm_path.replace('.webm', '.wav')
        subprocess.run([
            'ffmpeg', '-i', temp_webm_path,
            '-ar', str(TRANSCRIBE_SAMPLE_RATE),
            '-ac', '1',      # Mono
            '-y',            # Overwrite
            temp_wav_path
        ], capture_output=True, check=True)
        
        # Upload WAV to S3
        s3_key = f"audio/{file_id}.wav"
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        
        with open(temp_wav_path, 'rb') as wav_file:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=wav_file.read(),
                ContentType='audio/wav'
            )
        
        # Get WAV file size
        wav_size = os.path.getsize(temp_wav_path)
        print(f"WAV file size: {wav_size} bytes")
        
        # Cleanup temp files
        os.unlink(temp_webm_path)
        os.unlink(temp_wav_path)
        
        t2 = time.time()
        print(f"⏱️  Audio converted: {t2 - t1:.2f}s")
        print(f"Uploaded to S3: {s3_uri}")
        
        # Start transcription job
        job_name = f"transcribe-{file_id}"
        
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='wav',
            LanguageCode=TRANSCRIBE_LANGUAGE_CODE
        )
        t3 = time.time()
        print(f"⏱️  S3 upload + job start: {t3 - t2:.2f}s")
        print(f"Started transcription job: {job_name}")
        
        # Wait for transcription to complete (optimized polling)
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            print(f"Transcription status: {job_status}")
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            # Faster polling: 0.2s for first 10 attempts, then 0.5s
            time.sleep(0.2 if attempt < 10 else 0.5)
            attempt += 1
        
        if job_status == 'FAILED':
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown')
            print(f"Transcription FAILED: {failure_reason}")
            return JSONResponse({"error": f"Transcription failed: {failure_reason}"}, status_code=500)
        
        if job_status == 'COMPLETED':
            t4 = time.time()
            print(f"⏱️  Transcription completed: {t4 - t3:.2f}s")
            
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            import requests
            transcript_data = requests.get(transcript_uri).json()
            transcribed_text = transcript_data['results']['transcripts'][0]['transcript']
            print(f"Transcribed text: '{transcribed_text}'")
            
            # Cleanup
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            
            total_time = time.time() - start_time
            print(f"\n🎯 TOTAL LATENCY: {total_time:.2f}s\n")
            
            # Check if transcription is empty
            if not transcribed_text or transcribed_text.strip() == '':
                return JSONResponse({
                    "userText": "[No speech detected]",
                    "text": "I couldn't hear anything. Please speak louder and record for at least 2-3 seconds.",
                    "audioUrl": None
                })
            
            # Step 1: LLM identifies intent and function
            llm_result = process_user_input(transcribed_text)
            print(f"LLM identified function: {llm_result['function']}")
            
            function_name = llm_result["function"]
            params = llm_result["params"]
            
            # Step 2: Backend deterministically checks if OTP is required
            requires_otp = function_name in OTP_REQUIRED_FUNCTIONS
            print(f"OTP required: {requires_otp} (Backend security check)")
            
            if requires_otp:
                # Generate OTP and create session
                session_id = str(uuid.uuid4())
                otp = str(random.randint(100000, 999999))
                
                pending_sessions[session_id] = {
                    "function": function_name,
                    "params": params,
                    "otp": otp,
                    "timestamp": time.time()
                }
                
                print(f"\n🔐 OTP for session {session_id}: {otp}")
                print(f"   (Or use master OTP: {MASTER_OTP})\n")
                
                response_text = "For security, please enter the OTP sent to your registered device to complete this transaction."
                audio_url = text_to_speech(response_text)
                
                return JSONResponse({
                    "userText": transcribed_text,
                    "text": response_text,
                    "audioUrl": audio_url,
                    "requiresOTP": True,
                    "sessionId": session_id
                })
            
            # No OTP required - execute function directly
            response_text = execute_function(function_name, params)
            audio_url = text_to_speech(response_text)
            
            return JSONResponse({
                "userText": transcribed_text,
                "text": response_text,
                "audioUrl": audio_url
            })
        else:
            return JSONResponse({"error": "Transcription failed"}, status_code=500)
            
    except Exception as e:
        total_time = time.time() - start_time
        print(f"ERROR after {total_time:.2f}s: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
