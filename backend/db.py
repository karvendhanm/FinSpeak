"""
Database layer for FinSpeak
Handles all data persistence using SQLite
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional

DB_PATH = "finspeak.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ============================================================================
# ACCOUNTS
# ============================================================================

def get_all_accounts(user_id: str = "demo_user") -> List[Dict]:
    """Get all accounts for a user"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM accounts WHERE user_id = ?",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_account_by_id(account_id: str, user_id: str = "demo_user") -> Optional[Dict]:
    """Get account by ID"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM accounts WHERE id = ? AND user_id = ?",
            (account_id, user_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_account_balance(account_id: str) -> int:
    """Get current balance for account"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT balance FROM accounts WHERE id = ?",
            (account_id,)
        )
        row = cursor.fetchone()
        return row["balance"] if row else 0


def update_account_balance(account_id: str, new_balance: int):
    """Update account balance"""
    with get_db() as conn:
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, account_id)
        )


# ============================================================================
# BENEFICIARIES
# ============================================================================

def get_all_beneficiaries(user_id: str = "demo_user") -> List[Dict]:
    """Get all beneficiaries for a user"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM beneficiaries WHERE user_id = ?",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_beneficiary_by_id(beneficiary_id: str, user_id: str = "demo_user") -> Optional[Dict]:
    """Get beneficiary by ID"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM beneficiaries WHERE id = ? AND user_id = ?",
            (beneficiary_id, user_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def find_beneficiaries_by_name(name: str, user_id: str = "demo_user") -> List[Dict]:
    """Find beneficiaries matching a name (case-insensitive)"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM beneficiaries WHERE user_id = ? AND LOWER(name) LIKE ?",
            (user_id, f"%{name.lower()}%")
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# TRANSACTIONS
# ============================================================================

def add_transaction(account_id: str, txn_type: str, description: str, amount: int, balance_after: int):
    """Add a new transaction record"""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO transactions 
               (account_id, date, type, description, amount, balance_after)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                account_id,
                datetime.now().strftime("%Y-%m-%d"),
                txn_type,
                description,
                amount,
                balance_after
            )
        )


def get_transactions(account_id: str, limit: int = 10, start_date: str = None, end_date: str = None) -> List[Dict]:
    """Get transactions for account with optional date range
    
    Args:
        account_id: Account ID
        limit: Max number of transactions (default 10)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    with get_db() as conn:
        query = """SELECT date, type, description, amount, balance_after as balance
                   FROM transactions 
                   WHERE account_id = ?"""
        params = [account_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# TRANSFER OPERATIONS
# ============================================================================

def execute_transfer(from_account_id: str, to_beneficiary_id: str, amount: int, user_id: str = "demo_user") -> Dict:
    """
    Execute transfer: deduct from source, add transaction
    Returns: {"success": True, "new_balance": int, "beneficiary_name": str}
    """
    with get_db() as conn:
        # 1. Get source account
        cursor = conn.execute(
            "SELECT balance, name FROM accounts WHERE id = ? AND user_id = ?",
            (from_account_id, user_id)
        )
        account_row = cursor.fetchone()
        if not account_row:
            return {"success": False, "error": "Account not found"}
        
        current_balance = account_row["balance"]
        account_name = account_row["name"]
        
        # 2. Check sufficient balance
        if current_balance < amount:
            return {"success": False, "error": f"Insufficient balance. Available: ₹{current_balance:,}"}
        
        # 3. Get beneficiary
        cursor = conn.execute(
            "SELECT name FROM beneficiaries WHERE id = ? AND user_id = ?",
            (to_beneficiary_id, user_id)
        )
        ben_row = cursor.fetchone()
        if not ben_row:
            return {"success": False, "error": "Beneficiary not found"}
        
        ben_name = ben_row["name"]
        
        # 4. Deduct from source account
        new_balance = current_balance - amount
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, from_account_id)
        )
        
        # 5. Add transaction record
        conn.execute(
            """INSERT INTO transactions 
               (account_id, date, type, description, amount, balance_after)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                from_account_id,
                datetime.now().strftime("%Y-%m-%d"),
                "debit",
                f"Transfer to {ben_name}",
                amount,
                new_balance
            )
        )
        
        return {
            "success": True,
            "new_balance": new_balance,
            "beneficiary_name": ben_name,
            "account_name": account_name
        }


# ============================================================================
# UTILITY
# ============================================================================

def get_home_bank() -> str:
    """Get the home bank name"""
    return "Grace Hopper Bank"


def is_same_bank_transfer(beneficiary_id: str, user_id: str = "demo_user") -> bool:
    """Check if transfer is within the same bank"""
    beneficiary = get_beneficiary_by_id(beneficiary_id, user_id)
    if not beneficiary:
        return False
    return beneficiary["bank"] == get_home_bank()
