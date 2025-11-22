"""
Banking tools for Nidhi - Fund Transfer Only
"""
from strands.tools import tool
from mock_data import (
    get_user_accounts,
    get_user_beneficiaries,
    get_transfer_modes,
    get_account_by_id,
    get_beneficiary_by_id
)
import random

# Storage for pending transfers (used by initiate_transfer)
pending_transfers = {}


@tool
def get_accounts() -> list:
    """Get all user bank accounts with balances in rupees"""
    accounts = get_user_accounts()
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
def check_balance(account_type: str = None) -> dict:
    """Check account balance(s). If account_type is provided (e.g., 'savings', 'current'), return that specific account. Otherwise return all accounts with total.
    
    Args:
        account_type: Optional account type filter ('savings' or 'current')
    """
    accounts = get_user_accounts()
    
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
    beneficiaries = get_user_beneficiaries()
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
    from mock_data import get_transfer_modes as get_modes
    return get_modes()


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
    
    # Generate OTP and session
    otp = str(random.randint(100000, 999999))
    session_id = f"txn_{random.randint(10000, 99999)}"
    
    # Store pending transfer
    pending_transfers[session_id] = {
        "otp": otp,
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


# Export tools list for easy import
FUND_TRANSFER_TOOLS = [
    get_accounts,
    get_beneficiaries,
    get_transfer_modes,
    initiate_transfer
]

BALANCE_TOOLS = [
    check_balance
]

ALL_BANKING_TOOLS = FUND_TRANSFER_TOOLS + BALANCE_TOOLS
