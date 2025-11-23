"""
Audit logging system for FinSpeak
Tracks all banking operations for compliance and security
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager

AUDIT_DB = "finspeak_audit.db"

@contextmanager
def get_audit_db():
    conn = sqlite3.connect(AUDIT_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_audit_db():
    """Initialize audit log database"""
    with get_audit_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL,
                amount INTEGER,
                from_account TEXT,
                to_account TEXT,
                ip_address TEXT,
                session_id TEXT
            )
        """)

def log_action(user_id, action, status, details=None, amount=None, from_account=None, to_account=None, ip_address=None, session_id=None):
    """Log a banking action"""
    with get_audit_db() as conn:
        conn.execute("""
            INSERT INTO audit_logs 
            (timestamp, user_id, action, details, status, amount, from_account, to_account, ip_address, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_id,
            action,
            details,
            status,
            amount,
            mask_account(from_account) if from_account else None,
            mask_account(to_account) if to_account else None,
            ip_address,
            session_id
        ))

def mask_account(account_id):
    """Mask account ID for PII protection"""
    if not account_id or len(account_id) < 4:
        return account_id
    return f"***{account_id[-4:]}"

def get_audit_logs(user_id=None, limit=100):
    """Retrieve audit logs"""
    with get_audit_db() as conn:
        if user_id:
            cursor = conn.execute(
                "SELECT * FROM audit_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]

def get_metrics():
    """Get system metrics"""
    with get_audit_db() as conn:
        # Total completed transactions only
        total = conn.execute(
            "SELECT COUNT(*) as count FROM audit_logs WHERE action = 'transfer_completed'"
        ).fetchone()['count']
        
        # Success rate (completed transfers with success status)
        success = conn.execute(
            "SELECT COUNT(*) as count FROM audit_logs WHERE action = 'transfer_completed' AND status = 'success'"
        ).fetchone()['count']
        success_rate = (success / total * 100) if total > 0 else 0
        
        # Total amount transferred (only successful completed transfers)
        total_amount = conn.execute(
            "SELECT SUM(amount) as total FROM audit_logs WHERE action = 'transfer_completed' AND status = 'success'"
        ).fetchone()['total'] or 0
        
        # Recent activity (last 24h) - all actions
        recent = conn.execute(
            "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp > datetime('now', '-1 day')"
        ).fetchone()['count']
        
        return {
            "total_transactions": total,
            "success_rate": round(success_rate, 2),
            "total_amount_transferred": total_amount,
            "recent_activity_24h": recent
        }

# Initialize on import
init_audit_db()
