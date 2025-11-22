"""
FinSpeak FastAPI Server with Strands Agent
Simplified architecture for hackathon
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
import boto3
import uuid
import os
import time
import subprocess
import tempfile
import random
from config import (
    S3_BUCKET_NAME,
    MASTER_OTP,
    POLLY_VOICE_ID,
    POLLY_ENGINE,
    TRANSCRIBE_LANGUAGE_CODE,
    TRANSCRIBE_SAMPLE_RATE
)
from agent_prompt import SYSTEM_PROMPT
from banking_tools import ALL_BANKING_TOOLS, pending_transfers
from db import execute_transfer

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

# Bedrock Model for Strands
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-west-2",
    temperature=0,
)

# User agents (one per user)
user_agents = {}

# OTP storage
pending_otps = {}

def get_agent(user_id: str) -> Agent:
    """Get or create Strands agent for user"""
    if user_id not in user_agents:
        agent = Agent(
            name='nidhi_banking_assistant',
            model=bedrock_model,
            system_prompt=SYSTEM_PROMPT,
            tools=ALL_BANKING_TOOLS
        )
        
        user_agents[user_id] = agent
    
    return user_agents[user_id]

def text_to_speech(text):
    """Convert text to speech using AWS Polly"""
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

@app.post("/api/reset")
async def reset_session(userId: str = "demo_user"):
    """Reset user session"""
    if userId in user_agents:
        del user_agents[userId]
    return JSONResponse({"status": "reset"})

@app.post("/api/verify-otp")
async def verify_otp(otp: str, sessionId: str):
    """Verify OTP and complete transfer"""
    print(f"Verifying OTP: {otp} for session: {sessionId}")
    
    if sessionId not in pending_otps:
        return JSONResponse({"error": "No pending transaction"}, status_code=400)
    
    expected_otp = pending_otps[sessionId]["otp"]
    
    if otp == expected_otp or otp == MASTER_OTP:
        print(f"✅ OTP verified!")
        
        # Get transaction details
        txn_details = pending_otps[sessionId]["details"]
        
        # Execute the actual transfer in database
        try:
            result = execute_transfer(
                from_account_id=txn_details["from_account_id"],
                to_beneficiary_id=txn_details["to_beneficiary_id"],
                amount=txn_details["amount"]
            )
            
            if not result["success"]:
                print(f"❌ Transfer failed: {result['error']}")
                return JSONResponse({"error": result["error"]}, status_code=400)
            
            print(f"💰 Transfer executed! New balance: ₹{result['new_balance']:,}")
            
        except Exception as e:
            print(f"❌ Transfer execution error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": "Transfer failed"}, status_code=500)
        
        response_text = f"Transfer successful! {txn_details['amount']:,.0f} rupees sent to {txn_details['to_beneficiary']}."
        
        # Cleanup both pending_otps and pending_transfers
        del pending_otps[sessionId]
        if sessionId in pending_transfers:
            del pending_transfers[sessionId]
        
        audio_url = text_to_speech(response_text)
        
        return JSONResponse({
            "text": response_text,
            "audioUrl": audio_url,
            "workflowStatus": "COMPLETED",
            "showSuccessModal": True
        })
    else:
        print(f"❌ Invalid OTP")
        return JSONResponse({"error": "Invalid OTP"}, status_code=400)

def extract_options(text):
    """Extract clickable options from agent response"""
    import re
    options = []
    
    # Pattern: "- Option text" or "• Option text"
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            option = line.lstrip('-•').strip()
            if option:
                # Skip transaction lines (format: "DD MMM YYYY: Description ±₹Amount")
                if re.search(r'\d{1,2}\s+\w{3}\s+\d{4}:', option):
                    continue
                
                # Extract account with balance: "Savings Account ending with 7890 (₹10,00,000)"
                match = re.search(r'([\w\s]+?)\s+ending (?:with|in) (\d{4})\s*\(₹[\d,]+\)', option, re.IGNORECASE)
                if match:
                    acc_type = match.group(1).strip().title()
                    last_four = match.group(2)
                    option = f"{acc_type} (XXXX{last_four})"
                    options.append(option)
                    continue
                
                # Extract account without balance: "Savings Account ending with 7890"
                match = re.search(r'([\w\s]+?)\s+ending (?:with|in) (\d{4})', option, re.IGNORECASE)
                if match:
                    acc_type = match.group(1).strip().title()
                    last_four = match.group(2)
                    option = f"{acc_type} (XXXX{last_four})"
                    options.append(option)
                    continue
                
                # Skip only if line ends with balance info like ": ₹10,00,000"
                if re.search(r':\s*₹[\d,]+$', option):
                    continue
                
                # For other options (beneficiaries, transfer modes), keep as-is
                options.append(option)
    
    return options if options else None

def extract_confirmation_summary(text):
    """Extract transfer confirmation details"""
    import re
    
    # Pattern: "Send ₹X from Y to Z via MODE?" or "Send X rupees from Y to Z via MODE?"
    match = re.search(r'Send ₹?([\d,]+)(?:\s+rupees)? from ([^\n]+?) to ([^\n]+?) via (\w+)', text, re.IGNORECASE)
    if match:
        return {
            "amount": match.group(1),
            "from_account": match.group(2).strip(),
            "to_beneficiary": match.group(3).strip(),
            "mode": match.group(4).strip(),
            "needs_confirmation": True
        }
    return None

@app.post("/api/text")
async def process_text(text: str, userId: str = "demo_user"):
    """Process text input through Strands agent"""
    print(f"\n{'='*60}")
    print(f"User: {text}")
    
    try:
        agent = get_agent(userId)
        result = await agent.invoke_async(text)
        
        response_text = result.content if hasattr(result, 'content') else str(result)
        print(f"Agent: {response_text}")
        
        # Check if OTP is in response (from initiate_transfer tool)
        import re
        
        # Check if any new transfers were added to pending_transfers
        if pending_transfers:
            # Get the most recent session_id
            session_id = list(pending_transfers.keys())[-1]
            
            if session_id in pending_transfers and session_id not in pending_otps:
                transfer_data = pending_transfers[session_id]
                
                pending_otps[session_id] = {
                    "otp": transfer_data["otp"],
                    "details": {
                        "from_account_id": transfer_data["from_account_id"],
                        "to_beneficiary_id": transfer_data["to_beneficiary_id"],
                        "amount": transfer_data["amount"],
                        "to_beneficiary": transfer_data["to_beneficiary"]
                    }
                }
                
                print(f"\n{'='*60}")
                print(f"🔐 OTP GENERATED: {transfer_data['otp']}")
                print(f"   Master OTP: {MASTER_OTP}")
                print(f"   Session ID: {session_id}")
                print(f"{'='*60}\n")
                
                clean_text = f"An OTP has been sent to your registered mobile number. Please enter it to complete the transfer."
                audio_url = text_to_speech(clean_text)
                
                return JSONResponse({
                    "userText": text,
                    "text": clean_text,
                    "audioUrl": audio_url,
                    "requiresOTP": True,
                    "sessionId": session_id,
                    "workflowStatus": "WAITING_OTP"
                })
        
        # Extract options for buttons
        options = extract_options(response_text)
        
        # Extract confirmation summary
        confirmation = extract_confirmation_summary(response_text)
        
        # Check if response contains transaction history and pagination info
        transactions_data = None
        pagination_info = None
        if "transaction" in response_text.lower():
            import re
            from datetime import datetime
            txn_lines = []
            for line in response_text.split('\n'):
                # Match: "DD MMM YYYY: Description +₹Amount" or "- DD MMM YYYY: Description +₹Amount"
                match = re.search(r'-?\s*(\d{1,2}\s+\w{3}\s+\d{4}):\s*(.+?)\s+([+-])₹([\d,]+)', line)
                if match:
                    date_str, desc, sign, amount = match.groups()
                    # Convert "15 Jan 2025" to "15/01/2025"
                    date_obj = datetime.strptime(date_str, "%d %b %Y")
                    formatted_date = date_obj.strftime("%d/%m/%Y")
                    txn_lines.append({
                        "date": formatted_date,
                        "description": desc.strip(),
                        "type": "credit" if sign == "+" else "debit",
                        "amount": amount
                    })
            if txn_lines:
                transactions_data = txn_lines
                print(f"📊 Detected {len(txn_lines)} transactions")
                
                # No need to extract pagination for button navigation
        
        # Normal response
        audio_url = text_to_speech(response_text)
        
        response = {
            "userText": text,
            "text": response_text,
            "audioUrl": audio_url,
            "workflowStatus": "COMPLETED"
        }
        
        if options:
            response["options"] = [{"text": opt} for opt in options]
        
        if confirmation:
            response["confirmation"] = confirmation
        
        if transactions_data:
            response["transactions"] = transactions_data
            print(f"📤 Sending {len(transactions_data)} transactions")
        
        # Pagination handled via voice commands only
        
        print(f"📤 Full response keys: {response.keys()}")
        return JSONResponse(response)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/voice")
async def process_voice(audio: UploadFile = File(...)):
    """Process voice input via AWS Transcribe"""
    start_time = time.time()
    try:
        file_id = str(uuid.uuid4())
        audio_content = await audio.read()
        print(f"Received audio: {len(audio_content)} bytes")
        
        # Save and convert to WAV
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_webm:
            temp_webm.write(audio_content)
            temp_webm_path = temp_webm.name
        
        temp_wav_path = temp_webm_path.replace('.webm', '.wav')
        subprocess.run([
            'ffmpeg', '-i', temp_webm_path,
            '-ar', str(TRANSCRIBE_SAMPLE_RATE),
            '-ac', '1',
            '-y',
            temp_wav_path
        ], capture_output=True, check=True)
        
        # Upload to S3
        s3_key = f"audio/{file_id}.wav"
        s3_uri = f"s3://{S3_BUCKET_NAME}/{s3_key}"
        
        with open(temp_wav_path, 'rb') as wav_file:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=wav_file.read(),
                ContentType='audio/wav'
            )
        
        os.unlink(temp_webm_path)
        os.unlink(temp_wav_path)
        
        # Start transcription
        job_name = f"transcribe-{file_id}"
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='wav',
            LanguageCode=TRANSCRIBE_LANGUAGE_CODE
        )
        
        # Wait for completion
        max_attempts = 60
        attempt = 0
        while attempt < max_attempts:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status in ['COMPLETED', 'FAILED']:
                break
            
            time.sleep(0.2 if attempt < 10 else 0.5)
            attempt += 1
        
        if job_status == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            import requests
            transcript_data = requests.get(transcript_uri).json()
            transcribed_text = transcript_data['results']['transcripts'][0]['transcript']
            
            # Cleanup
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
            
            print(f"Transcribed: '{transcribed_text}' ({time.time() - start_time:.2f}s)")
            
            if not transcribed_text.strip():
                return JSONResponse({
                    "userText": "[No speech detected]",
                    "text": "I couldn't hear anything. Please try again.",
                    "audioUrl": None
                })
            
            return JSONResponse({"userText": transcribed_text})
        else:
            return JSONResponse({"error": "Transcription failed"}, status_code=500)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy", "architecture": "strands"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
