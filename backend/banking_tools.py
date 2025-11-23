"""
Banking tools for Nidhi - Fund Transfer and Balance Checking
"""
from strands.tools import tool
from db import (
    get_all_accounts,
    get_account_by_id,
    get_all_beneficiaries,
    get_beneficiary_by_id,
    find_beneficiaries_by_name,
    is_same_bank_transfer,
    get_transactions,
    execute_own_account_transfer
)
import random

# Storage for pending transfers (used by initiate_transfer)
pending_transfers = {}

# Storage for paginated transaction sessions
transaction_sessions = {}


@tool
def get_accounts() -> list:
    """Get all user bank accounts with current balances in rupees"""
    accounts = get_all_accounts()  # From database
    return [
        {
            "id": acc["id"],
            "display_name": f"{acc['name']} ({acc['account_number']})",
            "speech_name": f"{acc['type'].title()} Account ending with {acc['account_number'][-4:]}",
            "account_number": acc["account_number"],
            "balance": acc["balance"]
        }
        for acc in accounts
    ]


@tool
def get_destination_accounts(exclude_account_id: str) -> list:
    """Get user's accounts excluding the source account (for own-account transfers)
    
    Args:
        exclude_account_id: Account ID to exclude (the source account)
    """
    accounts = get_all_accounts()  # From database
    return [
        {
            "id": acc["id"],
            "display_name": f"{acc['name']} ({acc['account_number']})",
            "speech_name": f"{acc['type'].title()} Account ending with {acc['account_number'][-4:]}",
            "account_number": acc["account_number"],
            "balance": acc["balance"]
        }
        for acc in accounts if acc["id"] != exclude_account_id
    ]


@tool
def check_balance(account_type: str = None) -> dict:
    """Check account balance(s). If account_type is provided (e.g., 'savings', 'current'), return that specific account. Otherwise return all accounts with total.
    
    Args:
        account_type: Optional account type filter ('savings' or 'current')
    """
    accounts = get_all_accounts()  # From database
    
    if account_type:
        # Filter by account type
        account_type_lower = account_type.lower()
        filtered = [acc for acc in accounts if account_type_lower in acc["type"].lower() or account_type_lower in acc["name"].lower() or account_type_lower in acc["account_number"]]
        
        if not filtered:
            return {"error": f"No account found matching '{account_type}'"}
        
        return {
            "accounts": [
                {
                    "display_name": f"{acc['name']} ({acc['account_number']})",
                    "speech_name": f"{acc['type'].title()} Account ending with {acc['account_number'][-4:]}",
                    "balance": acc["balance"]
                }
                for acc in filtered
            ]
        }
    
    # Return all accounts with total
    total_balance = sum(acc["balance"] for acc in accounts)
    return {
        "accounts": [
            {
                "display_name": f"{acc['name']} ({acc['account_number']})",
                "speech_name": f"{acc['type'].title()} Account ending with {acc['account_number'][-4:]}",
                "balance": acc["balance"]
            }
            for acc in accounts
        ],
        "total_balance": total_balance
    }


@tool
def get_beneficiaries() -> list:
    """Get all saved beneficiaries"""
    beneficiaries = get_all_beneficiaries()  # From database
    return [
        {
            "id": ben["id"],
            "name": ben["name"],
            "bank": ben["bank"]
        }
        for ben in beneficiaries
    ]


@tool
def get_transfer_modes() -> list:
    """Get available transfer modes for inter-bank transfers"""
    return [
        {"id": "imps", "name": "IMPS", "description": "Instant (24x7)"},
        {"id": "neft", "name": "NEFT", "description": "Within 2 working hours"},
        {"id": "rtgs", "name": "RTGS", "description": "Real-time (₹2 lakh+, only in working hours)"}
    ]


@tool
def initiate_transfer(from_account_id: str, to_beneficiary_id: str, amount: float, mode: str = "imps") -> dict:
    """Initiate fund transfer after collecting all required information
    
    Args:
        from_account_id: Source account ID (e.g., acc_savings_primary)
        to_beneficiary_id: Beneficiary ID (e.g., ben_pratap_kumar)
        amount: Transfer amount in rupees
        mode: Transfer mode (imps/neft/rtgs), default is imps
    """
    # Validate account
    account = get_account_by_id(from_account_id)
    if not account:
        return {"error": "Source account not found"}
    
    if account["balance"] < amount:
        return {"error": f"Insufficient balance. Available: {account['balance']:,.0f} rupees"}
    
    # Validate beneficiary
    beneficiary = get_beneficiary_by_id(to_beneficiary_id)
    if not beneficiary:
        return {"error": "Beneficiary not found"}
    
    # Validate transfer mode limits
    mode_lower = mode.lower()
    if mode_lower == "imps" and amount > 500000:
        return {
            "error": f"IMPS supports transfers up to ₹5,00,000. Your amount: ₹{amount:,.0f}",
            "suggestion": "Please use NEFT (any amount) or RTGS (₹2 lakh+) for this transfer."
        }
    elif mode_lower == "rtgs" and amount < 200000:
        return {
            "error": f"RTGS requires minimum ₹2,00,000. Your amount: ₹{amount:,.0f}",
            "suggestion": "Please use IMPS (up to ₹5 lakh) or NEFT (any amount) for this transfer."
        }
    
    # Generate OTP and session
    otp = str(random.randint(100000, 999999))
    session_id = f"txn_{random.randint(10000, 99999)}"
    
    # Store pending transfer with IDs for database execution
    pending_transfers[session_id] = {
        "otp": otp,
        "from_account_id": from_account_id,
        "to_beneficiary_id": to_beneficiary_id,
        "from_account": account["name"],
        "to_beneficiary": beneficiary["name"],
        "amount": amount
    }
    
    return {
        "status": "otp_required",
        "session_id": session_id,
        "otp": otp,
        "message": f"Transfer of {amount:,.0f} rupees from {account['name']} to {beneficiary['name']} is ready. An OTP has been sent to the registered mobile number."
    }


@tool
def initiate_own_account_transfer(from_account_id: str, to_account_id: str, amount: float) -> dict:
    """Initiate transfer between user's own accounts (instant, no mode selection needed)
    
    Args:
        from_account_id: Source account ID (e.g., acc_current)
        to_account_id: Destination account ID (e.g., acc_savings_primary)
        amount: Transfer amount in rupees
    """
    # Validate source account
    from_account = get_account_by_id(from_account_id)
    if not from_account:
        return {"error": "Source account not found"}
    
    if from_account["balance"] < amount:
        return {"error": f"Insufficient balance. Available: {from_account['balance']:,.0f} rupees"}
    
    # Validate destination account
    to_account = get_account_by_id(to_account_id)
    if not to_account:
        return {"error": "Destination account not found"}
    
    # Prevent same account transfer
    if from_account_id == to_account_id:
        return {"error": "Cannot transfer to the same account"}
    
    # Generate OTP and session
    otp = str(random.randint(100000, 999999))
    session_id = f"txn_{random.randint(10000, 99999)}"
    
    # Store pending transfer with IDs for database execution
    pending_transfers[session_id] = {
        "otp": otp,
        "transfer_type": "own_account",
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "from_account": from_account["name"],
        "to_account": to_account["name"],
        "amount": amount
    }
    
    return {
        "status": "otp_required",
        "session_id": session_id,
        "otp": otp,
        "message": f"Transfer of {amount:,.0f} rupees from {from_account['name']} to {to_account['name']} is ready. An OTP has been sent to the registered mobile number."
    }


# Export tools list for easy import
FUND_TRANSFER_TOOLS = [
    get_accounts,
    get_destination_accounts,
    get_beneficiaries,
    get_transfer_modes,
    initiate_transfer,
    initiate_own_account_transfer
]

@tool
def get_transaction_history(account_id: str = None, account_type: str = None, date_range: str = None, start_date: str = None, end_date: str = None, page: int = 1) -> dict:
    """Get transaction history for an account with optional date filtering and pagination.
    
    Args:
        account_id: Specific account ID (e.g., 'acc_savings_primary')
        account_type: Account type or account number to filter (e.g., 'savings', '7890')
        date_range: Relative date range (e.g., 'last 2 weeks', 'last month', 'last 3 months')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        page: Page number (default: 1, shows 5 transactions per page)
    
    Note: Maximum date range is 3 months. Results are paginated with 5 transactions per page.
    """
    from datetime import datetime, timedelta
    
    accounts = get_all_accounts()
    
    # Find the target account
    target_account = None
    if account_id:
        target_account = get_account_by_id(account_id)
    elif account_type:
        account_type_lower = account_type.lower()
        for acc in accounts:
            if (account_type_lower in acc["type"].lower() or 
                account_type_lower in acc["name"].lower() or 
                account_type_lower in acc["account_number"]):
                target_account = acc
                break
    
    if not target_account:
        return {"error": "Account not found. Please specify which account."}
    
    # Parse date range
    if date_range:
        from dateutil.relativedelta import relativedelta
        import re
        
        today = datetime.now()
        date_range_lower = date_range.lower()
        
        # Parse relative dates with flexible patterns
        if 'week' in date_range_lower:
            match = re.search(r'(\d+)\s*weeks?', date_range_lower)
            weeks = int(match.group(1)) if match else 1
            start_date = (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        elif 'month' in date_range_lower:
            match = re.search(r'(\d+)\s*months?', date_range_lower)
            months = int(match.group(1)) if match else 1
            if months > 3:
                return {"error": "Maximum date range is 3 months."}
            start_date = (today - relativedelta(months=months)).strftime('%Y-%m-%d')
        elif 'day' in date_range_lower:
            match = re.search(r'(\d+)\s*days?', date_range_lower)
            days = int(match.group(1)) if match else 7
            start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        else:
            return {"error": "Please specify a valid date range (e.g., 'last 2 weeks', 'last month', 'last 5 days')."}
        
        end_date = today.strftime('%Y-%m-%d')
    
    # Validate 3-month limit
    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if (end - start).days > 90:
            return {"error": "Maximum date range is 3 months (90 days)."}
    
    # Get transactions from database
    all_transactions = get_transactions(target_account["id"], limit=100, start_date=start_date, end_date=end_date)
    
    if not all_transactions:
        date_info = f" for the specified period" if start_date or end_date else ""
        return {
            "account": {
                "display_name": f"{target_account['name']} ({target_account['account_number']})",
                "speech_name": f"{target_account['type'].title()} Account ending with {target_account['account_number'][-4:]}"
            },
            "transactions": [],
            "message": f"No transactions found{date_info}."
        }
    
    # Pagination: 5 transactions per page
    page_size = 5
    total_transactions = len(all_transactions)
    total_pages = (total_transactions + page_size - 1) // page_size
    page = max(1, min(page, total_pages))  # Clamp page number
    
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_transactions)
    paginated_transactions = all_transactions[start_idx:end_idx]
    
    # Store session for pagination
    import uuid
    session_id = str(uuid.uuid4())
    transaction_sessions[session_id] = {
        "account_id": target_account["id"],
        "account_type": account_type,
        "date_range": date_range,
        "start_date": start_date,
        "end_date": end_date,
        "total_transactions": total_transactions,
        "total_pages": total_pages,
        "current_page": page
    }
    
    # Format transactions for display
    return {
        "account": {
            "display_name": f"{target_account['name']} ({target_account['account_number']})",
            "speech_name": f"{target_account['type'].title()} Account ending with {target_account['account_number'][-4:]}"
        },
        "transactions": [
            {
                "date": txn["date"],
                "type": txn["type"],
                "description": txn["description"],
                "amount": txn["amount"],
                "balance": txn["balance"]
            }
            for txn in paginated_transactions
        ],
        "pagination": {
            "session_id": session_id,
            "current_page": page,
            "total_pages": total_pages,
            "total_transactions": total_transactions,
            "showing": f"{start_idx + 1}-{end_idx} of {total_transactions}"
        },
        "date_range": {"start": start_date, "end": end_date} if start_date or end_date else None
    }


@tool
def get_loan_details() -> dict:
    """Get user's active loans with EMI, outstanding amount, and interest rates"""
    return {
        "loans": [
            {
                "type": "Home Loan",
                "outstanding": 2500000,
                "emi": 25000,
                "due_date": "5th of every month",
                "interest_rate": "8.5%",
                "tenure_remaining": "15 years"
            },
            {
                "type": "Personal Loan",
                "outstanding": 150000,
                "emi": 5000,
                "due_date": "10th of every month",
                "interest_rate": "12%",
                "tenure_remaining": "2 years 6 months"
            }
        ]
    }

@tool
def get_credit_card_details() -> dict:
    """Get credit card details including limit, balance, and payment due"""
    return {
        "cards": [
            {
                "name": "Grace Hopper Platinum Card",
                "card_number": "XXXX5678",
                "credit_limit": 500000,
                "used_amount": 45000,
                "available_credit": 455000,
                "payment_due_date": "15th of every month",
                "minimum_due": 2250,
                "total_due": 45000
            }
        ]
    }

BALANCE_TOOLS = [
    check_balance
]

@tool
def get_upcoming_payments() -> dict:
    """Get upcoming bill payments, EMIs, and due dates"""
    from datetime import datetime, timedelta
    
    today = datetime.now()
    
    return {
        "upcoming": [
            {
                "type": "Home Loan EMI",
                "amount": 25000,
                "due_date": "2025-12-05",
                "days_left": (datetime(2025, 12, 5) - today).days
            },
            {
                "type": "Personal Loan EMI",
                "amount": 5000,
                "due_date": "2025-12-10",
                "days_left": (datetime(2025, 12, 10) - today).days
            },
            {
                "type": "Credit Card Payment",
                "amount": 2250,
                "due_date": "2025-12-15",
                "days_left": (datetime(2025, 12, 15) - today).days
            },
            {
                "type": "Electricity Bill",
                "amount": 850,
                "due_date": "2025-12-01",
                "days_left": (datetime(2025, 12, 1) - today).days
            }
        ]
    }

LOAN_CREDIT_TOOLS = [
    get_loan_details,
    get_credit_card_details,
    get_upcoming_payments
]

@tool
def next_page(session_id: str = None) -> dict:
    """Navigate to the next page of transaction history.
    
    Args:
        session_id: Transaction session ID from previous get_transaction_history call
    """
    if not session_id or session_id not in transaction_sessions:
        return {"error": "No active transaction history session. Please request transaction history first."}
    
    session = transaction_sessions[session_id]
    if session["current_page"] >= session["total_pages"]:
        return {"error": f"Already on the last page ({session['total_pages']})."}
    
    # Call get_transaction_history with next page
    return get_transaction_history(
        account_id=session["account_id"],
        date_range=session["date_range"],
        start_date=session["start_date"],
        end_date=session["end_date"],
        page=session["current_page"] + 1
    )

@tool
def previous_page(session_id: str = None) -> dict:
    """Navigate to the previous page of transaction history.
    
    Args:
        session_id: Transaction session ID from previous get_transaction_history call
    """
    if not session_id or session_id not in transaction_sessions:
        return {"error": "No active transaction history session. Please request transaction history first."}
    
    session = transaction_sessions[session_id]
    if session["current_page"] <= 1:
        return {"error": "Already on the first page."}
    
    # Call get_transaction_history with previous page
    return get_transaction_history(
        account_id=session["account_id"],
        date_range=session["date_range"],
        start_date=session["start_date"],
        end_date=session["end_date"],
        page=session["current_page"] - 1
    )

TRANSACTION_TOOLS = [
    get_transaction_history,
    next_page,
    previous_page
]

ALL_BANKING_TOOLS = FUND_TRANSFER_TOOLS + BALANCE_TOOLS + TRANSACTION_TOOLS + LOAN_CREDIT_TOOLS
