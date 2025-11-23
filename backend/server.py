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
from db import execute_transfer, execute_own_account_transfer, get_account_by_id
from audit_logger import log_action, get_audit_logs, get_metrics
from risk_monitor import analyze_transaction

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
async def verify_otp(otp: str, sessionId: str, userId: str = "demo_user"):
    """Verify OTP and complete transfer"""
    print(f"Verifying OTP: {otp} for session: {sessionId}")
    
    # Log OTP verification attempt
    log_action(userId, "otp_verification", "attempted", session_id=sessionId)
    
    if sessionId not in pending_otps:
        return JSONResponse({"error": "No pending transaction"}, status_code=400)
    
    expected_otp = pending_otps[sessionId]["otp"]
    
    if otp == expected_otp or otp == MASTER_OTP:
        print(f"✅ OTP verified!")
        log_action(userId, "otp_verification", "success", session_id=sessionId)
        
        # Get transaction details
        txn_details = pending_otps[sessionId]["details"]
        transfer_type = txn_details.get("transfer_type", "beneficiary")
        
        # Execute the actual transfer in database
        try:
            if transfer_type == "own_account":
                # Own account transfer
                result = execute_own_account_transfer(
                    from_account_id=txn_details["from_account_id"],
                    to_account_id=txn_details["to_account_id"],
                    amount=txn_details["amount"]
                )
                
                if not result["success"]:
                    print(f"❌ Transfer failed: {result['error']}")
                    return JSONResponse({"error": result["error"]}, status_code=400)
                
                print(f"💰 Own account transfer executed!")
                print(f"   Transaction ID: {result['transaction_id']}")
                print(f"   From: {result['from_account']} - New balance: ₹{result['from_balance']:,}")
                print(f"   To: {result['to_account']} - New balance: ₹{result['to_balance']:,}")
                
                # Log successful transfer
                log_action(
                    userId, "transfer_completed", "success",
                    details=f"TXN {result['transaction_id']}: {result['from_account_number']} -> {result['to_account_number']}",
                    amount=txn_details['amount'],
                    from_account=txn_details['from_account_id'],
                    to_account=txn_details['to_account_id'],
                    session_id=sessionId
                )
                
                from_speech = f"{result['from_account_type']} Account ending with {result['from_account_number'][-4:]}"
                to_speech = f"{result['to_account_type']} Account ending with {result['to_account_number'][-4:]}"
                response_text = f"Transfer successful! {txn_details['amount']:,.0f} rupees transferred from {from_speech} to {to_speech}.\n\nTransaction ID: {result['transaction_id']}"
            else:
                # Beneficiary transfer (existing flow)
                result = execute_transfer(
                    from_account_id=txn_details["from_account_id"],
                    to_beneficiary_id=txn_details["to_beneficiary_id"],
                    amount=txn_details["amount"]
                )
                
                if not result["success"]:
                    print(f"❌ Transfer failed: {result['error']}")
                    return JSONResponse({"error": result["error"]}, status_code=400)
                
                print(f"💰 Transfer executed!")
                print(f"   Transaction ID: {result['transaction_id']}")
                print(f"   New balance: ₹{result['new_balance']:,}")
                
                # Log successful transfer
                # Get source account number for better logging
                from_acc = get_account_by_id(txn_details['from_account_id'])
                from_acc_num = from_acc['account_number'] if from_acc else 'Unknown'
                
                log_action(
                    userId, "transfer_completed", "success",
                    details=f"TXN {result['transaction_id']}: {from_acc_num} -> {txn_details['to_beneficiary']}",
                    amount=txn_details['amount'],
                    from_account=txn_details['from_account_id'],
                    to_account=txn_details['to_beneficiary_id'],
                    session_id=sessionId
                )
                
                response_text = f"Transfer successful! {txn_details['amount']:,.0f} rupees sent to {txn_details['to_beneficiary']}.\n\nTransaction ID: {result['transaction_id']}"
            
        except Exception as e:
            print(f"❌ Transfer execution error: {e}")
            import traceback
            traceback.print_exc()
            
            # Log failed transfer
            log_action(
                userId, "transfer_failed", "failed",
                details=f"Transfer execution error: {str(e)}",
                session_id=sessionId
            )
            
            return JSONResponse({"error": "Transfer failed"}, status_code=500)
        
        # Cleanup both pending_otps and pending_transfers
        del pending_otps[sessionId]
        if sessionId in pending_transfers:
            del pending_transfers[sessionId]
        
        audio_url = text_to_speech(response_text)
        
        return JSONResponse({
            "text": response_text,
            "audioUrl": audio_url,
            "workflowStatus": "COMPLETED",
            "showSuccessModal": True,
            "celebration": True
        })
    else:
        print(f"❌ Invalid OTP")
        log_action(userId, "otp_verification", "failed", details="Invalid OTP", session_id=sessionId)
        return JSONResponse({"error": "Invalid OTP"}, status_code=400)

def extract_options(text):
    """Extract clickable options from agent response"""
    import re
    options = []
    
    # Check for transfer type selection (special case)
    if "sending money to a registered beneficiary or to one of your own accounts" in text.lower():
        return [{"text": "To a registered beneficiary"}, {"text": "To my own account"}]
    
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
                
                # Skip informational lines (loan/credit/payment details, etc.)
                # These contain colons with values like "Outstanding: ₹25,00,000" or "EMI: ₹25,000"
                if ':' in option and ('₹' in option or 'due on' in option.lower() or '%' in option or 'year' in option.lower() or 'month' in option.lower()):
                    continue
                
                # Skip payment reminder lines (format: "Type ₹amount due on date (X days left)")
                if '₹' in option and 'due on' in option.lower() and ('day' in option.lower() or 'left' in option.lower()):
                    continue
                
                # Skip only if line ends with balance info like ": ₹10,00,000"
                if re.search(r':\s*₹[\d,]+$', option):
                    continue
                
                # For other options (beneficiaries, transfer modes), keep as-is
                options.append(option)
    
    # Return formatted options or None
    if options:
        return [{"text": opt} for opt in options]
    return None

def extract_confirmation_summary(text):
    """Extract transfer confirmation details"""
    import re
    
    # Pattern for beneficiary transfer: "Send ₹X from Y to Z via MODE?"
    match = re.search(r'Send ₹?([\d,]+)(?:\s+rupees)? from ([^\n]+?) to ([^\n]+?) via (\w+)', text, re.IGNORECASE)
    if match:
        return {
            "amount": match.group(1),
            "from_account": match.group(2).strip(),
            "to_beneficiary": match.group(3).strip(),
            "mode": match.group(4).strip(),
            "transfer_type": "beneficiary",
            "needs_confirmation": True
        }
    
    # Pattern for own-account transfer: "Transfer ₹X from Y to Z?"
    match = re.search(r'Transfer ₹?([\d,]+)(?:\s+rupees)? from ([^.?]+?) to ([^.?]+?)(?:\.|\?)', text, re.IGNORECASE)
    if match:
        to_account = match.group(3).strip()
        return {
            "amount": match.group(1),
            "from_account": match.group(2).strip(),
            "to_beneficiary": to_account,  # Use to_beneficiary for consistency with frontend
            "to_account": to_account,
            "transfer_type": "own_account",
            "needs_confirmation": True
        }
    
    return None

@app.post("/api/text")
async def process_text(text: str, userId: str = "demo_user"):
    """Process text input through Strands agent"""
    print(f"\n{'='*60}")
    print(f"📥 INCOMING REQUEST - User: {text}")
    print(f"   User ID: {userId}")
    print(f"   Timestamp: {time.time()}")
    
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
                transfer_type = transfer_data.get("transfer_type", "beneficiary")
                
                if transfer_type == "own_account":
                    # Own account transfer
                    pending_otps[session_id] = {
                        "otp": transfer_data["otp"],
                        "details": {
                            "transfer_type": "own_account",
                            "from_account_id": transfer_data["from_account_id"],
                            "to_account_id": transfer_data["to_account_id"],
                            "amount": transfer_data["amount"],
                            "from_account": transfer_data["from_account"],
                            "to_account": transfer_data["to_account"]
                        }
                    }
                else:
                    # Beneficiary transfer (existing flow)
                    pending_otps[session_id] = {
                        "otp": transfer_data["otp"],
                        "details": {
                            "transfer_type": "beneficiary",
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
                
                # Log transfer initiation
                log_action(
                    userId, "transfer_initiated", "pending",
                    details=f"Amount: ₹{transfer_data['amount']:,}",
                    amount=transfer_data['amount'],
                    session_id=session_id
                )
                
                # Risk analysis
                risk_analysis = analyze_transaction(
                    userId,
                    transfer_data['amount'],
                    transfer_data.get('to_beneficiary_id'),
                    transfer_data.get('transfer_type', 'beneficiary'),
                    from_account_id=transfer_data.get('from_account_id'),
                    to_account_id=transfer_data.get('to_account_id')
                )
                
                if risk_analysis['has_risks']:
                    print(f"⚠️ RISK ALERT: {risk_analysis['overall_risk']} risk detected")
                    for risk in risk_analysis['risks']:
                        print(f"   - {risk['reason']}")
                    log_action(userId, "risk_alert", "flagged", details=str(risk_analysis['risks']))
                
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
        
        # Extract confirmation summary first (takes precedence)
        confirmation = extract_confirmation_summary(response_text)
        
        # Extract options for buttons (only if not a confirmation)
        options = None if confirmation else extract_options(response_text)
        
        # Check if response contains loan details
        loans_data = None
        if "loan" in response_text.lower() and ("outstanding" in response_text.lower() or "emi" in response_text.lower()):
            import re
            loan_lines = []
            for line in response_text.split('\n'):
                # Match: "Type Loan: Outstanding ₹X, EMI ₹Y due on Z, Interest rate A%, B remaining"
                match = re.search(r'(.+?)\s+Loan:\s*Outstanding\s*₹([\d,]+),\s*EMI\s*₹([\d,]+)\s+due on\s+(.+?),\s*Interest rate\s+([\d.]+)%,\s+(.+?)$', line, re.IGNORECASE)
                if match:
                    loan_type, outstanding, emi, due_date, interest_rate, tenure = match.groups()
                    loan_lines.append({
                        "type": loan_type.strip(),
                        "outstanding": outstanding,
                        "emi": emi,
                        "due_date": due_date.strip(),
                        "interest_rate": interest_rate,
                        "tenure_remaining": tenure.strip()
                    })
            if loan_lines:
                loans_data = loan_lines
                print(f"🏦 Detected {len(loan_lines)} loans")
        
        # Check if response contains credit card details
        cards_data = None
        if "credit card" in response_text.lower() or "card ending" in response_text.lower():
            import re
            card_lines = []
            for line in response_text.split('\n'):
                # Match: "Card Name ending with XXXX: Available credit ₹X of ₹Y, Current bill ₹Z (Minimum payment ₹W), Payment due on D"
                match = re.search(r'(.+?)\s+ending with\s+(\d{4}):\s*Available credit\s*₹([\d,]+)\s+of\s+₹([\d,]+),\s*Current bill\s*₹([\d,]+)\s*\(Minimum payment\s*₹([\d,]+)\),\s*Payment due on\s+(.+)', line, re.IGNORECASE)
                if match:
                    card_name, last_four, available, limit, total_due, min_due, due_date = match.groups()
                    card_lines.append({
                        "name": card_name.strip(),
                        "last_four": last_four,
                        "available_credit": available,
                        "credit_limit": limit,
                        "total_due": total_due,
                        "minimum_due": min_due,
                        "due_date": due_date.strip()
                    })
            if card_lines:
                cards_data = card_lines
                print(f"💳 Detected {len(card_lines)} credit cards")
        
        # Check if response contains payment reminders
        payments_data = None
        if ("bill" in response_text.lower() or "payment" in response_text.lower()) and "due on" in response_text.lower():
            import re
            payment_lines = []
            for line in response_text.split('\n'):
                # Match: "Type ₹amount due on date (X days left)"
                match = re.search(r'-\s*(.+?)\s+₹([\d,]+)\s+due on\s+(.+?)\s+\((\d+)\s+days?\s+left\)', line, re.IGNORECASE)
                if match:
                    payment_type, amount, due_date, days_left = match.groups()
                    payment_lines.append({
                        "type": payment_type.strip(),
                        "amount": amount,
                        "due_date": due_date.strip(),
                        "days_left": int(days_left)
                    })
            if payment_lines:
                payments_data = payment_lines
                print(f"📅 Detected {len(payment_lines)} upcoming payments")
        
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
            response["options"] = options
        
        if confirmation:
            response["confirmation"] = confirmation
        
        if transactions_data:
            response["transactions"] = transactions_data
            print(f"📤 Sending {len(transactions_data)} transactions")
        
        if loans_data:
            response["loans"] = loans_data
            print(f"📤 Sending {len(loans_data)} loans")
        
        if cards_data:
            response["cards"] = cards_data
            print(f"📤 Sending {len(cards_data)} credit cards")
        
        if payments_data:
            response["payments"] = payments_data
            print(f"📤 Sending {len(payments_data)} payments")
        
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

@app.get("/api/metrics")
async def metrics():
    """Get system metrics and audit logs"""
    return JSONResponse(get_metrics())

@app.get("/api/audit-logs")
async def audit_logs(userId: str = None, limit: int = 50):
    """Get audit logs for monitoring"""
    logs = get_audit_logs(userId, limit)
    return JSONResponse({"logs": logs, "count": len(logs)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
