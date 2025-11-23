"""
Risk monitoring and anomaly detection for FinSpeak
Flags suspicious transactions for security
"""
from datetime import datetime, timedelta
from audit_logger import get_audit_logs

# Risk thresholds
HIGH_AMOUNT_THRESHOLD = 50000  # ₹50,000
RAPID_TRANSFER_WINDOW = 300  # 5 minutes
MAX_TRANSFERS_IN_WINDOW = 3
NEW_BENEFICIARY_AMOUNT_LIMIT = 25000  # ₹25,000

def check_high_amount(amount, transfer_type="beneficiary"):
    """Flag high-value transactions (only for beneficiary transfers)"""
    # Skip risk check for own account transfers
    if transfer_type == "own_account":
        return None
    
    if amount >= HIGH_AMOUNT_THRESHOLD:
        return {
            "risk_level": "HIGH",
            "reason": f"High-value transaction: ₹{amount:,}",
            "recommendation": "Additional verification recommended"
        }
    return None

def check_rapid_transfers(user_id):
    """Detect multiple transfers in short time"""
    logs = get_audit_logs(user_id, limit=10)
    recent_transfers = [
        log for log in logs 
        if log['action'] == 'transfer_initiated' 
        and datetime.fromisoformat(log['timestamp']) > datetime.now() - timedelta(seconds=RAPID_TRANSFER_WINDOW)
    ]
    
    if len(recent_transfers) >= MAX_TRANSFERS_IN_WINDOW:
        return {
            "risk_level": "MEDIUM",
            "reason": f"{len(recent_transfers)} transfers in {RAPID_TRANSFER_WINDOW//60} minutes",
            "recommendation": "Verify user identity"
        }
    return None

def check_new_beneficiary(beneficiary_id, amount, user_id):
    """Flag large transfers to new beneficiaries"""
    logs = get_audit_logs(user_id, limit=100)
    
    # Check if beneficiary has been used before
    previous_transfers = [
        log for log in logs 
        if log['action'] == 'transfer_completed' 
        and beneficiary_id in (log['details'] or '')
    ]
    
    if not previous_transfers and amount > NEW_BENEFICIARY_AMOUNT_LIMIT:
        return {
            "risk_level": "MEDIUM",
            "reason": f"First transfer to new beneficiary: ₹{amount:,}",
            "recommendation": "Confirm beneficiary details"
        }
    return None

def analyze_transaction(user_id, amount, beneficiary_id=None, transfer_type="beneficiary"):
    """Comprehensive risk analysis"""
    risks = []
    
    # Skip all risk checks for own account transfers
    if transfer_type == "own_account":
        return {"has_risks": False, "overall_risk": "LOW"}
    
    # Check high amount (only for beneficiary transfers)
    risk = check_high_amount(amount, transfer_type)
    if risk:
        risks.append(risk)
    
    # Check rapid transfers
    risk = check_rapid_transfers(user_id)
    if risk:
        risks.append(risk)
    
    # Check new beneficiary (only for beneficiary transfers)
    if transfer_type == "beneficiary" and beneficiary_id:
        risk = check_new_beneficiary(beneficiary_id, amount, user_id)
        if risk:
            risks.append(risk)
    
    if risks:
        return {
            "has_risks": True,
            "risks": risks,
            "overall_risk": max([r['risk_level'] for r in risks], key=lambda x: ['LOW', 'MEDIUM', 'HIGH'].index(x))
        }
    
    return {"has_risks": False, "overall_risk": "LOW"}
