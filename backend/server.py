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
from config import (
    S3_BUCKET_NAME,
    MASTER_OTP,
    POLLY_VOICE_ID,
    POLLY_ENGINE,
    TRANSCRIBE_LANGUAGE_CODE,
    TRANSCRIBE_SAMPLE_RATE
)
from session_manager import create_session, get_session, update_session, set_waiting, set_completed, delete_session
from workflows import transfer_money_workflow, check_balance_workflow, transaction_history_workflow
from system_prompt import create_system_prompt
from functions import get_available_functions_for_state, format_functions_for_llm, banking_functions
from sops import banking_base_sop, get_available_sops
from mock_data import HOME_BANK, get_user_accounts, get_user_beneficiaries
from llm_handler import call_bedrock_llm, parse_llm_response

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

# User sessions (maps user_id to session_id)
user_sessions = {}

def call_llm(system_prompt, user_message, available_functions):
    """Call LLM with system prompt and user message. Returns parsed response."""
    llm_output = call_bedrock_llm(system_prompt, user_message)
    parsed = parse_llm_response(llm_output)
    print(f"LLM Thinking: {parsed['thinking'][:100]}..." if len(parsed['thinking']) > 100 else f"LLM Thinking: {parsed['thinking']}")
    return parsed

def execute_workflow(function_name, session_id, user_input=None):
    """Execute workflow function and return result"""
    session = get_session(session_id)
    
    if function_name == "transfer_money_workflow":
        return transfer_money_workflow(session_id=session_id, user_input=user_input)
    elif function_name == "check_balance_workflow":
        return check_balance_workflow(session_id=session_id, user_input=user_input)
    elif function_name == "transaction_history_workflow":
        return transaction_history_workflow(session_id=session_id, user_input=user_input)
    elif function_name == "cancel_workflow":
        delete_session(session_id)
        return {
            "message": "Workflow cancelled. How else can I help you?",
            "workflow_status": "CANCELLED"
        }
    else:
        return {
            "message": "I'm not sure how to help with that.",
            "workflow_status": "COMPLETED"
        }

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
    
    session = get_session(sessionId)
    if not session:
        return JSONResponse({"error": "Invalid or expired session"}, status_code=400)
    
    # Get OTP from session metadata
    expected_otp = session.get("metadata", {}).get("otp")
    if not expected_otp:
        return JSONResponse({"error": "No OTP found for this session"}, status_code=400)
    
    # Validate OTP
    if otp == expected_otp or otp == MASTER_OTP:
        print(f"✅ OTP verified! Resuming workflow")
        
        # Resume workflow with OTP confirmation
        result = execute_workflow(session["current_function"], sessionId, user_input="OTP_VERIFIED")
        
        response_text = result["response_text"]
        audio_url = text_to_speech(response_text)
        
        return JSONResponse({
            "text": response_text,
            "audioUrl": audio_url,
            "workflowStatus": result.get("workflow_status")
        })
    else:
        print(f"❌ Invalid OTP")
        return JSONResponse({"error": "Invalid OTP. Please try again."}, status_code=400)

@app.post("/api/text")
async def process_text(text: str, userId: str = "demo_user"):
    print(f"\n{'='*60}")
    print(f"Received text: {text}")
    print(f"User ID: {userId}")
    
    # Get or create session for user
    session_id = user_sessions.get(userId)
    if not session_id:
        session_id = create_session(workflow="conversation", user_id=userId)
        user_sessions[userId] = session_id
        print(f"Created new session: {session_id}")
    else:
        print(f"Using existing session: {session_id}")
    
    session = get_session(session_id)
    workflow_status = session.get("status")  # session_manager stores as 'status' not 'workflow_status'
    print(f"Workflow status: {workflow_status}")
    
    # If workflow is WAITING, let LLM process the input and decide what to do
    if workflow_status == "WAITING":
        print(f"Workflow waiting for: {session.get('required_input', [])}")
        
        # Build system prompt with current workflow context
        workflow_context = f"\n\n<CRITICAL_INSTRUCTION>\nThe workflow is currently WAITING for user input.\nWorkflow: {session['current_function']}\nWaiting for: {session.get('required_input', [])}\nCurrent metadata: {session.get('metadata', {})}\n\nYou MUST call the 'resume_workflow' function to continue the workflow with the user's response.\nProcess the user's input according to the SOP instructions and resume the workflow.\n</CRITICAL_INSTRUCTION>\n"
        
        # Get SOPs as content strings
        from sops import transfer_money_sop, check_balance_sop, transaction_history_sop
        sub_sops_content = "\n\n".join([
            transfer_money_sop["content"],
            check_balance_sop["content"],
            transaction_history_sop["content"]
        ])
        
        system_prompt = create_system_prompt(
            agent_name=f"{HOME_BANK} Voice Assistant",
            agent_purpose="Help users with banking operations through natural voice conversations",
            agent_sop=banking_base_sop["content"] + workflow_context,
            agent_sub_sops=sub_sops_content,
            agent_tools=format_functions_for_llm()
        )
        
        # Get available functions (includes resume_workflow)
        available_functions = get_available_functions_for_state(workflow_status)
        
        # Call LLM to decide what to do
        llm_response = call_llm(system_prompt, text, available_functions)
        function_name = llm_response.get("function_name")
        
        print(f"LLM selected function: {function_name}")
        
        if function_name == "resume_workflow" or function_name == session['current_function']:
            # LLM wants to resume - extract parameters from thinking or parse user input
            print(f"Resuming workflow: {session['current_function']}")
            required_input = session.get("required_input", [])
            
            # Parse user input based on what's required
            parsed_input = {}
            if "amount" in required_input:
                # Extract amount from text
                import re
                amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                if amount_match:
                    parsed_input["amount"] = float(amount_match.group(1).replace(',', ''))
            elif "beneficiary_name" in required_input:
                parsed_input["beneficiary_name"] = text.strip()
            elif "from_account" in required_input or "account_id" in required_input:
                # User selected an account - extract account ID from display text or voice input
                accounts = get_user_accounts()
                matched_account = None
                text_lower = text.lower()
                for acc in accounts:
                    # Match by account number, name, or partial name
                    if (acc["account_number"] in text or 
                        acc["name"].lower() in text_lower or 
                        text_lower in acc["name"].lower() or
                        acc["account_number"][-4:] in text):
                        matched_account = acc["id"]
                        break
                parsed_input[required_input[0]] = matched_account if matched_account else text.strip()
            elif "beneficiary_id" in required_input:
                # Match beneficiary by ID or name
                from mock_data import get_user_beneficiaries
                beneficiaries = get_user_beneficiaries()
                matched_ben = None
                text_lower = text.lower()
                for ben in beneficiaries:
                    if (ben["id"] in text or 
                        ben["name"].lower() in text_lower or
                        ben["bank"].lower() in text_lower):
                        matched_ben = ben["id"]
                        break
                parsed_input["beneficiary_id"] = matched_ben if matched_ben else text.strip()
            elif "transfer_mode" in required_input:
                # Match transfer mode by name
                text_lower = text.lower()
                if "imps" in text_lower or "instant" in text_lower:
                    parsed_input["transfer_mode"] = "imps"
                elif "neft" in text_lower:
                    parsed_input["transfer_mode"] = "neft"
                elif "rtgs" in text_lower or "real" in text_lower:
                    parsed_input["transfer_mode"] = "rtgs"
                else:
                    parsed_input["transfer_mode"] = text.strip().lower()
            elif "time_period" in required_input:
                parsed_input["time_period"] = text.strip()
            
            result = execute_workflow(session["current_function"], session_id, user_input=parsed_input)
        elif function_name == "cancel_workflow":
            result = execute_workflow("cancel_workflow", session_id)
        else:
            result = {
                "message": "I'm here to help. Please provide the information requested.",
                "workflow_status": workflow_status
            }
    elif workflow_status == "RUNNING" or workflow_status is None:
        # Build system prompt
        from sops import transfer_money_sop, check_balance_sop, transaction_history_sop
        sub_sops_content = "\n\n".join([
            transfer_money_sop["content"],
            check_balance_sop["content"],
            transaction_history_sop["content"]
        ])
        
        system_prompt = create_system_prompt(
            agent_name=f"{HOME_BANK} Voice Assistant",
            agent_purpose="Help users with banking operations through natural voice conversations",
            agent_sop=banking_base_sop["content"],
            agent_sub_sops=sub_sops_content,
            agent_tools=format_functions_for_llm()
        )
        
        # Get available functions
        available_functions = get_available_functions_for_state(workflow_status)
        
        # Call LLM
        llm_response = call_llm(system_prompt, text, available_functions)
        function_name = llm_response.get("function_name")
        
        print(f"LLM selected function: {function_name}")
        
        if function_name and function_name in banking_functions:
            # Update session with current function and workflow
            update_session(session_id, current_function=function_name, workflow=function_name)
            
            # Execute workflow with initial user input
            result = execute_workflow(function_name, session_id, user_input=text)
        else:
            result = {
                "response_text": "I'm here to help with your banking needs. You can check your balance, transfer money, or view transaction history.",
                "workflow_status": "COMPLETED"
            }
    
    response_text = result.get("message", result.get("response_text", "I'm here to help."))
    workflow_status = result.get("workflow_status")
    
    print(f"Response: {response_text}")
    print(f"New workflow status: {workflow_status}")
    
    # Check if OTP is required (workflow is waiting for OTP)
    requires_otp = "otp" in result.get("required_input", [])
    if requires_otp:
        otp = str(random.randint(100000, 999999))
        update_session(session_id, metadata={"otp": otp})
        print(f"\n🔐 OTP for session {session_id}: {otp}")
        print(f"   (Or use master OTP: {MASTER_OTP})\n")
    
    # Convert to speech
    audio_url = text_to_speech(response_text)
    
    response = {
        "userText": text,
        "text": response_text,
        "audioUrl": audio_url,
        "workflowStatus": workflow_status
    }
    
    # Include options if workflow returned them
    if "options" in result:
        response["options"] = result["options"]
    
    # Include confirmation message if present
    if "confirmation" in result:
        response["confirmation"] = result["confirmation"]
    
    if requires_otp:
        response["requiresOTP"] = True
        response["sessionId"] = session_id
    
    print(f"{'='*60}\n")
    return JSONResponse(response)

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
            
            # Return only transcribed text - frontend will call /api/text for LLM processing
            return JSONResponse({
                "userText": transcribed_text
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
