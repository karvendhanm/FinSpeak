# Mock data for FinSpeak demo

import re
from datetime import datetime, timedelta

HOME_BANK = "Grace Hopper Bank"

DEMO_USER = {
    "user_id": "demo_user",
    "name": "Demo User",
    "bank": HOME_BANK,
    "accounts": [
        {
            "id": "acc_savings_primary",
            "name": "Primary Savings",
            "type": "savings",
            "account_number": "XXXX7890",
            "balance": 12450.75,
            "bank": HOME_BANK
        },
        {
            "id": "acc_savings_emergency",
            "name": "Emergency Fund",
            "type": "savings",
            "account_number": "XXXX3456",
            "balance": 25000.00,
            "bank": HOME_BANK
        },
        {
            "id": "acc_current",
            "name": "Current Account",
            "type": "current",
            "account_number": "XXXX1234",
            "balance": 5230.00,
            "bank": HOME_BANK
        }
    ],
    "beneficiaries": [
        {
            "id": "ben_pratap_kumar",
            "name": "Pratap Kumar",
            "account_number": "XXXX1234",
            "bank": "HDFC Bank"
        },
        {
            "id": "ben_pratap_singh",
            "name": "Pratap Singh",
            "account_number": "XXXX5678",
            "bank": HOME_BANK  # Same bank - no transfer mode needed
        },
        {
            "id": "ben_raj_sharma",
            "name": "Raj Sharma",
            "account_number": "XXXX9012",
            "bank": "SBI"
        }
    ]
}

def get_user_accounts(user_id="demo_user"):
    """Get user accounts"""
    return DEMO_USER["accounts"]

def get_user_beneficiaries(user_id="demo_user"):
    """Get all beneficiaries for user"""
    return DEMO_USER["beneficiaries"]

def find_beneficiaries_by_name(name, user_id="demo_user"):
    """Find beneficiaries matching a name (case-insensitive partial match)"""
    name_lower = name.lower()
    return [
        b for b in DEMO_USER["beneficiaries"]
        if name_lower in b["name"].lower()
    ]

def get_account_by_id(account_id, user_id="demo_user"):
    """Get account by ID"""
    for acc in DEMO_USER["accounts"]:
        if acc["id"] == account_id:
            return acc
    return None

def get_beneficiary_by_id(beneficiary_id, user_id="demo_user"):
    """Get beneficiary by ID"""
    for ben in DEMO_USER["beneficiaries"]:
        if ben["id"] == beneficiary_id:
            return ben
    return None

def is_same_bank_transfer(beneficiary_id, user_id="demo_user"):
    """Check if transfer is within the same bank (no transfer mode needed)"""
    beneficiary = get_beneficiary_by_id(beneficiary_id, user_id)
    if not beneficiary:
        return False
    return beneficiary["bank"] == HOME_BANK

def get_transfer_modes():
    """Get available transfer modes for inter-bank transfers"""
    return [
        {"id": "imps", "name": "IMPS", "description": "Instant (24x7)"},
        {"id": "neft", "name": "NEFT", "description": "Within 2 hours (working hours)"},
        {"id": "rtgs", "name": "RTGS", "description": "Real-time (₹2 lakh+, working hours)"}
    ]

# Mock transaction data
from datetime import datetime, timedelta

def generate_transactions(account_id, from_date=None, to_date=None, days=30):
    """Generate mock transactions for an account within date range"""
    
    # Base transactions for Primary Savings Account
    primary_savings_transactions = [
        {"date": "2025-01-15", "type": "credit", "description": "Salary Credit", "amount": 5000.00, "balance": 12450.75},
        {"date": "2025-01-12", "type": "debit", "description": "Amazon Purchase", "amount": 150.25, "balance": 7450.75},
        {"date": "2025-01-10", "type": "debit", "description": "Electricity Bill", "amount": 85.50, "balance": 7601.00},
        {"date": "2025-01-08", "type": "credit", "description": "Transfer from Raj Sharma", "amount": 200.00, "balance": 7686.50},
        {"date": "2025-01-05", "type": "debit", "description": "ATM Withdrawal", "amount": 500.00, "balance": 7486.50},
        {"date": "2025-01-03", "type": "debit", "description": "Grocery Store", "amount": 120.75, "balance": 7986.50},
        {"date": "2025-01-01", "type": "credit", "description": "Interest Credit", "amount": 25.50, "balance": 8107.25},
        {"date": "2024-12-28", "type": "debit", "description": "Restaurant", "amount": 75.00, "balance": 8081.75},
        {"date": "2024-12-25", "type": "debit", "description": "Online Shopping", "amount": 250.00, "balance": 8156.75},
        {"date": "2024-12-20", "type": "credit", "description": "Freelance Payment", "amount": 1000.00, "balance": 8406.75}
    ]
    
    # Base transactions for Emergency Fund
    emergency_fund_transactions = [
        {"date": "2025-01-15", "type": "credit", "description": "Monthly Savings Transfer", "amount": 2000.00, "balance": 25000.00},
        {"date": "2025-01-01", "type": "credit", "description": "Interest Credit", "amount": 45.50, "balance": 23000.00},
        {"date": "2024-12-15", "type": "credit", "description": "Monthly Savings Transfer", "amount": 2000.00, "balance": 22954.50},
        {"date": "2024-12-01", "type": "credit", "description": "Interest Credit", "amount": 42.30, "balance": 20954.50},
        {"date": "2024-11-15", "type": "credit", "description": "Monthly Savings Transfer", "amount": 2000.00, "balance": 20912.20}
    ]
    
    # Base transactions for Current Account
    current_transactions = [
        {"date": "2025-01-14", "type": "debit", "description": "Rent Payment", "amount": 1200.00, "balance": 5230.00},
        {"date": "2025-01-11", "type": "credit", "description": "Transfer from Savings", "amount": 2000.00, "balance": 6430.00},
        {"date": "2025-01-09", "type": "debit", "description": "Gas Station", "amount": 60.00, "balance": 4430.00},
        {"date": "2025-01-06", "type": "debit", "description": "Coffee Shop", "amount": 15.50, "balance": 4490.00},
        {"date": "2025-01-04", "type": "debit", "description": "Pharmacy", "amount": 45.25, "balance": 4505.50},
        {"date": "2025-01-02", "type": "credit", "description": "Refund", "amount": 30.00, "balance": 4550.75},
        {"date": "2024-12-30", "type": "debit", "description": "Utility Bill", "amount": 95.00, "balance": 4520.75},
        {"date": "2024-12-27", "type": "debit", "description": "Movie Tickets", "amount": 40.00, "balance": 4615.75},
        {"date": "2024-12-23", "type": "debit", "description": "Book Store", "amount": 55.00, "balance": 4655.75},
        {"date": "2024-12-18", "type": "credit", "description": "Cashback", "amount": 20.00, "balance": 4710.75}
    ]
    
    # Select transactions based on account
    if account_id == "acc_savings_primary":
        all_transactions = primary_savings_transactions
    elif account_id == "acc_savings_emergency":
        all_transactions = emergency_fund_transactions
    elif account_id == "acc_current":
        all_transactions = current_transactions
    else:
        return []
    
    # Filter by date range if provided
    if from_date or to_date:
        filtered = []
        for txn in all_transactions:
            txn_date = datetime.strptime(txn["date"], "%Y-%m-%d")
            
            if from_date and to_date:
                if from_date <= txn_date <= to_date:
                    filtered.append(txn)
            elif from_date:
                if txn_date >= from_date:
                    filtered.append(txn)
            elif to_date:
                if txn_date <= to_date:
                    filtered.append(txn)
        return filtered
    
    # Return last N days if specified
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = [txn for txn in all_transactions 
                   if datetime.strptime(txn["date"], "%Y-%m-%d") >= cutoff_date]
        return filtered[:5]  # Return max 5 transactions
    
    return all_transactions[:5]  # Default: return 5 most recent

def parse_time_period(time_period_str):
    """Parse natural language time period to date range"""
    now = datetime.now()
    time_period_lower = time_period_str.lower()
    
    # Last N days/weeks/months
    if "last" in time_period_lower:
        if "week" in time_period_lower:
            # Extract number of weeks
            import re
            match = re.search(r'(\d+)\s*week', time_period_lower)
            weeks = int(match.group(1)) if match else 1
            from_date = now - timedelta(weeks=weeks)
            return from_date, now
        elif "day" in time_period_lower:
            match = re.search(r'(\d+)\s*day', time_period_lower)
            days = int(match.group(1)) if match else 7
            from_date = now - timedelta(days=days)
            return from_date, now
        elif "month" in time_period_lower:
            match = re.search(r'(\d+)\s*month', time_period_lower)
            months = int(match.group(1)) if match else 1
            from_date = now - timedelta(days=months*30)
            return from_date, now
    
    # This week/month
    if "this week" in time_period_lower:
        from_date = now - timedelta(days=now.weekday())
        return from_date, now
    elif "this month" in time_period_lower:
        from_date = now.replace(day=1)
        return from_date, now
    
    # Default: last 7 days
    return now - timedelta(days=7), now
