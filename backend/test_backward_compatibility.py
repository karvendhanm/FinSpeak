"""Test backward compatibility - ensure pagination doesn't break existing features"""
from banking_tools import (
    get_accounts, 
    check_balance, 
    get_beneficiaries, 
    get_transfer_modes,
    get_transaction_history
)

print("Testing backward compatibility...\n")

# Test 1: Check balance (no changes)
print("1. Testing check_balance()...")
result = check_balance()
assert "accounts" in result
assert "total_balance" in result
print("   ✅ check_balance works")

# Test 2: Get accounts (no changes)
print("2. Testing get_accounts()...")
accounts = get_accounts()
assert len(accounts) > 0
assert "id" in accounts[0]
print("   ✅ get_accounts works")

# Test 3: Get beneficiaries (no changes)
print("3. Testing get_beneficiaries()...")
beneficiaries = get_beneficiaries()
assert len(beneficiaries) > 0
assert "name" in beneficiaries[0]
print("   ✅ get_beneficiaries works")

# Test 4: Get transfer modes (no changes)
print("4. Testing get_transfer_modes()...")
modes = get_transfer_modes()
assert len(modes) > 0
assert "id" in modes[0]
print("   ✅ get_transfer_modes works")

# Test 5: Transaction history with default page (backward compatible)
print("5. Testing get_transaction_history() with defaults...")
result = get_transaction_history(account_type="savings", date_range="last month")
assert "transactions" in result
assert "pagination" in result  # New field
assert result["pagination"]["current_page"] == 1
print("   ✅ get_transaction_history works with pagination")

# Test 6: Transaction history with explicit page=1 (same as default)
print("6. Testing get_transaction_history() with page=1...")
result = get_transaction_history(account_type="savings", date_range="last month", page=1)
assert "transactions" in result
assert result["pagination"]["current_page"] == 1
print("   ✅ Explicit page=1 works")

# Test 7: Transaction history with few results (< 5 transactions)
print("7. Testing get_transaction_history() with few results...")
result = get_transaction_history(account_type="emergency", date_range="last month")
assert "transactions" in result
# Should still have pagination even with few results
assert "pagination" in result
print("   ✅ Works with few transactions")

# Test 8: Transaction history with no results
print("8. Testing get_transaction_history() with no results...")
result = get_transaction_history(account_type="savings", start_date="2020-01-01", end_date="2020-01-31")
assert "transactions" in result
assert len(result["transactions"]) == 0
assert "message" in result
print("   ✅ Works with no transactions")

print("\n✅ All backward compatibility tests passed!")
print("   - Existing functions work without changes")
print("   - Pagination is added without breaking old behavior")
print("   - Default page=1 maintains backward compatibility")
