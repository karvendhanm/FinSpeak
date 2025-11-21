"""
Workflow Orchestrator for FinSpeak Banking Assistant
Handles multi-turn conversation workflows
"""

import random
from session_manager import (
    create_session, get_session, update_session, 
    set_waiting, set_completed, WorkflowStatus
)
from mock_data import (
    get_user_accounts, find_beneficiaries_by_name, 
    get_account_by_id, get_beneficiary_by_id,
    is_same_bank_transfer, get_transfer_modes,
    generate_transactions, parse_time_period
)

def transfer_money_workflow(amount=None, beneficiary_name=None, session_id=None, user_input=None):
    """
    Handle money transfer workflow with multi-turn conversation
    
    Flow:
    1. Get amount and beneficiary name
    2. Select from_account (if multiple)
    3. Disambiguate beneficiary (if multiple matches)
    4. Select transfer_mode (if different bank)
    5. OTP verification
    6. Execute transfer
    """
    
    # Resume existing session or create new
    if session_id:
        session = get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Update with user input (only if it's a dict)
        if user_input and isinstance(user_input, dict):
            update_session(session_id, metadata=user_input)
        # If user_input is a string (initial message), try to extract amount and beneficiary
        elif user_input and isinstance(user_input, str):
            import re
            # Extract amount
            amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_input)
            if amount_match:
                update_session(session_id, metadata={"amount": float(amount_match.group(1).replace(',', ''))})
            # Extract beneficiary name (words after "to" or "pay")
            beneficiary_match = re.search(r'(?:to|pay)\s+([A-Za-z\s]+?)(?:\s|$)', user_input, re.IGNORECASE)
            if beneficiary_match:
                update_session(session_id, metadata={"beneficiary_name": beneficiary_match.group(1).strip()})
    else:
        # Create new session
        session_id = create_session("transfer_money", {
            "amount": amount,
            "beneficiary_name": beneficiary_name
        })
        session = get_session(session_id)
    
    metadata = session["metadata"]
    
    # Step 1: Check if we have amount
    if not metadata.get("amount"):
        set_waiting(session_id, ["amount"])
        return {
            "session_id": session_id,
            "workflow_status": WorkflowStatus.WAITING,
            "required_input": ["amount"],
            "message": "How much would you like to transfer?"
        }
    
    # Step 2: Check if we have beneficiary name
    if not metadata.get("beneficiary_name"):
        set_waiting(session_id, ["beneficiary_name"])
        return {
            "session_id": session_id,
            "workflow_status": WorkflowStatus.WAITING,
            "required_input": ["beneficiary_name"],
            "message": "Who would you like to send money to?"
        }
    
    # Step 3: Select from_account
    if not metadata.get("from_account"):
        accounts = get_user_accounts()
        if len(accounts) > 1:
            set_waiting(session_id, ["from_account"])
            account_list = ", ".join([f"{acc['name']} ending with {acc['account_number'][-4:]}" for acc in accounts])
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["from_account"],
                "message": f"Which account would you like to use? Your options are: {account_list}",
                "options": [
                    {
                        "id": acc["id"],
                        "text": f"{acc['name']} ({acc['account_number']}) - ${acc['balance']:,.2f}",
                        "display": f"{acc['name']} {acc['account_number']}"
                    }
                    for acc in accounts
                ]
            }
        else:
            # Only one account, auto-select
            update_session(session_id, metadata={"from_account": accounts[0]["id"]})
            metadata["from_account"] = accounts[0]["id"]
    
    # If we just got from_account, show confirmation
    if metadata.get("from_account") and not metadata.get("from_account_confirmed"):
        account = get_account_by_id(metadata["from_account"])
        update_session(session_id, metadata={"from_account_confirmed": True})
        # Continue to next step but don't return yet
    
    # Step 4: Disambiguate beneficiary
    if not metadata.get("beneficiary_id"):
        beneficiaries = find_beneficiaries_by_name(metadata["beneficiary_name"])
        
        if len(beneficiaries) == 0:
            set_completed(session_id)
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.COMPLETED,
                "message": f"Sorry, I couldn't find a beneficiary named '{metadata['beneficiary_name']}'. Please add them first."
            }
        elif len(beneficiaries) > 1:
            set_waiting(session_id, ["beneficiary_id"])
            account = get_account_by_id(metadata["from_account"])
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["beneficiary_id"],
                "confirmation": f"Account selected: {account['name']} {account['account_number']}",
                "message": f"I found {len(beneficiaries)} beneficiaries named {metadata['beneficiary_name']}. " + ", ".join([f"{ben['name']} at {ben['bank']}" for ben in beneficiaries]) + ". Which one would you like to proceed with?",
                "options": [
                    {
                        "id": ben["id"],
                        "text": f"{ben['name']} - {ben['bank']} ({ben['account_number']})",
                        "display": ben["id"]
                    }
                    for ben in beneficiaries
                ]
            }
        else:
            # Only one match, auto-select
            update_session(session_id, metadata={"beneficiary_id": beneficiaries[0]["id"]})
            metadata["beneficiary_id"] = beneficiaries[0]["id"]
    
    # If we just got beneficiary_id, show confirmation
    if metadata.get("beneficiary_id") and not metadata.get("beneficiary_confirmed"):
        beneficiary = get_beneficiary_by_id(metadata["beneficiary_id"])
        update_session(session_id, metadata={"beneficiary_confirmed": True})
        # Continue to next step but don't return yet
    
    # Step 5: Select transfer mode (if different bank)
    if not metadata.get("transfer_mode"):
        if not is_same_bank_transfer(metadata["beneficiary_id"]):
            # Different bank - need transfer mode
            set_waiting(session_id, ["transfer_mode"])
            transfer_modes = get_transfer_modes()
            account = get_account_by_id(metadata["from_account"])
            beneficiary = get_beneficiary_by_id(metadata["beneficiary_id"])
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["transfer_mode"],
                "confirmation": f"Account selected: {account['name']} {account['account_number']}\nPayee: {beneficiary['name']} ({beneficiary['id']})",
                "message": "This is an inter-bank transfer. You can choose IMPS for instant transfer, NEFT for transfer within 2 hours, or RTGS for real-time transfer. Which would you prefer?",
                "options": [
                    {
                        "id": mode["id"],
                        "text": f"{mode['name']} - {mode['description']}",
                        "display": mode["id"]
                    }
                    for mode in transfer_modes
                ]
            }
        else:
            # Same bank - no transfer mode needed
            update_session(session_id, metadata={"transfer_mode": "internal"})
            metadata["transfer_mode"] = "internal"
    
    # If we just got transfer_mode, show confirmation
    if metadata.get("transfer_mode") and not metadata.get("transfer_mode_confirmed"):
        update_session(session_id, metadata={"transfer_mode_confirmed": True})
        # Continue to next step but don't return yet
    
    # Step 6: OTP verification
    if not metadata.get("otp_verified"):
        if not metadata.get("otp"):
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            update_session(session_id, metadata={"otp": otp})
            
            set_waiting(session_id, ["otp"])
            account = get_account_by_id(metadata["from_account"])
            beneficiary = get_beneficiary_by_id(metadata["beneficiary_id"])
            mode_display = metadata.get("transfer_mode", "internal").upper()
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["otp"],
                "confirmation": f"Account selected: {account['name']} {account['account_number']}\nPayee: {beneficiary['name']} ({beneficiary['id']})\nTransfer mode: {mode_display}",
                "message": "Please enter the OTP sent to your registered device.",
                "otp": otp  # For demo purposes
            }
    
    # Step 7: Execute transfer
    set_completed(session_id)
    
    account = get_account_by_id(metadata["from_account"])
    beneficiary = get_beneficiary_by_id(metadata["beneficiary_id"])
    
    return {
        "session_id": session_id,
        "workflow_status": WorkflowStatus.COMPLETED,
        "message": f"Transfer successful! ${metadata['amount']} sent to {beneficiary['name']} at {beneficiary['bank']} from your {account['name']}.",
        "transaction_details": {
            "amount": metadata["amount"],
            "from_account": account["name"],
            "to_beneficiary": beneficiary["name"],
            "to_bank": beneficiary["bank"],
            "transfer_mode": metadata.get("transfer_mode", "internal").upper()
        }
    }

def check_balance_workflow(session_id=None, user_input=None):
    """
    Handle balance inquiry workflow
    
    Flow:
    1. Select account (if multiple)
    2. Return balance
    """
    
    # Resume existing session or create new
    if session_id:
        session = get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        if user_input and isinstance(user_input, dict):
            update_session(session_id, metadata=user_input)
    else:
        session_id = create_session("check_balance", {})
        session = get_session(session_id)
    
    metadata = session["metadata"]
    
    # Step 1: Select account
    if not metadata.get("account_id"):
        accounts = get_user_accounts()
        if len(accounts) > 1:
            set_waiting(session_id, ["account_id"])
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["account_id"],
                "message": "Which account would you like to check?",
                "options": [
                    {
                        "id": acc["id"],
                        "text": f"{acc['name']} ({acc['account_number']})",
                        "display": f"{acc['name']} {acc['account_number']}"
                    }
                    for acc in accounts
                ]
            }
        else:
            # Only one account
            metadata["account_id"] = accounts[0]["id"]
            update_session(session_id, metadata={"account_id": accounts[0]["id"]})
    
    # Step 2: Return balance
    set_completed(session_id)
    account = get_account_by_id(metadata["account_id"])
    
    return {
        "session_id": session_id,
        "workflow_status": WorkflowStatus.COMPLETED,
        "message": f"Your {account['name']} has a balance of ${account['balance']:,.2f}",
        "balance": account["balance"],
        "account_name": account["name"]
    }

def transaction_history_workflow(time_period=None, session_id=None, user_input=None):
    """
    Handle transaction history workflow
    
    Flow:
    1. Select account (if multiple)
    2. Get time period (if not provided)
    3. Return transactions
    """
    
    # Resume existing session or create new
    if session_id:
        session = get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        if user_input and isinstance(user_input, dict):
            update_session(session_id, metadata=user_input)
    else:
        session_id = create_session("transaction_history", {
            "time_period": time_period
        })
        session = get_session(session_id)
    
    metadata = session["metadata"]
    
    # Step 1: Select account
    if not metadata.get("account_id"):
        accounts = get_user_accounts()
        if len(accounts) > 1:
            set_waiting(session_id, ["account_id"])
            return {
                "session_id": session_id,
                "workflow_status": WorkflowStatus.WAITING,
                "required_input": ["account_id"],
                "message": "Which account's transactions would you like to see?",
                "options": [
                    {
                        "id": acc["id"],
                        "text": f"{acc['name']} ({acc['account_number']})",
                        "display": f"{acc['name']} {acc['account_number']}"
                    }
                    for acc in accounts
                ]
            }
        else:
            metadata["account_id"] = accounts[0]["id"]
            update_session(session_id, metadata={"account_id": accounts[0]["id"]})
    
    # Step 2: Get time period
    if not metadata.get("time_period"):
        set_waiting(session_id, ["time_period"])
        return {
            "session_id": session_id,
            "workflow_status": WorkflowStatus.WAITING,
            "required_input": ["time_period"],
            "message": "What time period? For example: last 7 days, last 3 weeks, or this month",
            "options": [
                {"id": "last_7_days", "text": "Last 7 days"},
                {"id": "last_30_days", "text": "Last 30 days"},
                {"id": "this_month", "text": "This month"}
            ]
        }
    
    # Step 3: Get transactions
    set_completed(session_id)
    
    # Parse time period
    from_date, to_date = parse_time_period(metadata["time_period"])
    
    # Get transactions
    transactions = generate_transactions(
        metadata["account_id"],
        from_date=from_date,
        to_date=to_date
    )
    
    account = get_account_by_id(metadata["account_id"])
    
    return {
        "session_id": session_id,
        "workflow_status": WorkflowStatus.COMPLETED,
        "message": f"Here are your recent transactions for {account['name']}:",
        "transactions": transactions,
        "count": len(transactions),
        "time_period": metadata["time_period"]
    }
