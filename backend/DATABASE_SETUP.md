# Database Setup Guide

## Overview
FinSpeak now uses SQLite for data persistence. All account balances, transactions, and beneficiaries are stored in a database.

## Setup Steps

### 1. Initialize Database
```bash
cd backend
python init_db.py
```

This will create `finspeak.db` with:
- ✅ 3 demo accounts with initial balances
- ✅ 3 beneficiaries
- ✅ Sample transaction history

### 2. Start Server
```bash
python server.py
```

## What's Persistent Now

### ✅ Account Balances
- Balances update in real-time when transfers complete
- Survives server restarts

### ✅ Transaction History
- Every transfer creates a transaction record
- Includes date, description, amount, and balance after

### ✅ Beneficiaries
- All saved beneficiaries stored in database

## Database Schema

### accounts
```sql
- id (TEXT): Account ID
- user_id (TEXT): User ID
- name (TEXT): Account name (e.g., "Primary Savings")
- type (TEXT): Account type (savings/current)
- account_number (TEXT): Masked number (XXXX7890)
- balance (INTEGER): Balance in rupees
- bank (TEXT): Bank name
```

### beneficiaries
```sql
- id (TEXT): Beneficiary ID
- user_id (TEXT): User ID
- name (TEXT): Beneficiary name
- account_number (TEXT): Account number
- bank (TEXT): Bank name
```

### transactions
```sql
- id (INTEGER): Auto-increment ID
- account_id (TEXT): Related account
- date (TEXT): Transaction date
- type (TEXT): credit or debit
- description (TEXT): Transaction description
- amount (INTEGER): Amount in rupees
- balance_after (INTEGER): Balance after transaction
- created_at (TIMESTAMP): Record creation time
```

## Testing the Database

### Test Transfer Flow
```bash
# 1. Check initial balance
User: "What's my balance?"
# Should show ₹10,00,000 for Primary Savings

# 2. Make a transfer
User: "Send 5000 to Pratap Kumar"
# Complete the flow with OTP

# 3. Check balance again
User: "What's my balance?"
# Should show ₹9,95,000 (deducted 5000)

# 4. Check transaction history
User: "Show my recent transactions"
# Should show the transfer as latest transaction
```

## Resetting Database

To reset to initial state:
```bash
rm finspeak.db
python init_db.py
```

## Database Location
- File: `backend/finspeak.db`
- Excluded from git (in .gitignore)
- Portable - can copy to backup/restore

## Migration from mock_data.py

All functions now use database:
- ❌ `mock_data.get_user_accounts()` → ✅ `db.get_all_accounts()`
- ❌ `mock_data.get_user_beneficiaries()` → ✅ `db.get_all_beneficiaries()`
- ❌ `mock_data.get_account_by_id()` → ✅ `db.get_account_by_id()`
- ❌ `mock_data.generate_transactions()` → ✅ `db.get_transactions()`

## Benefits

✅ **Real Updates**: Transfers actually deduct money  
✅ **Persistent**: Data survives server restarts  
✅ **Transaction History**: Every action is recorded  
✅ **ACID Transactions**: Safe, atomic database operations  
✅ **No External Dependencies**: SQLite is built into Python  
✅ **Easy Backup**: Just copy the .db file
