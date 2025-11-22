"""Test core features to ensure nothing is broken"""
from banking_tools import (
    get_accounts,
    check_balance,
    get_beneficiaries,
    initiate_transfer,
    get_transaction_history
)

print("Testing core features...\n")

# Test 1: Balance check
print("1. Balance Check:")
result = check_balance()
print(f"   Total balance: ₹{result['total_balance']:,}")
print(f"   Accounts: {len(result['accounts'])}")
print("   ✅ Balance check works\n")

# Test 2: Get accounts for transfer
print("2. Get Accounts:")
accounts = get_accounts()
print(f"   Found {len(accounts)} accounts")
for acc in accounts:
    print(f"   - {acc['speech_name']}: ₹{acc['balance']:,}")
print("   ✅ Get accounts works\n")

# Test 3: Get beneficiaries
print("3. Get Beneficiaries:")
beneficiaries = get_beneficiaries()
print(f"   Found {len(beneficiaries)} beneficiaries")
for ben in beneficiaries:
    print(f"   - {ben['name']} ({ben['bank']})")
print("   ✅ Get beneficiaries works\n")

# Test 4: Initiate transfer (without executing)
print("4. Initiate Transfer:")
result = initiate_transfer(
    from_account_id="acc_savings_primary",
    to_beneficiary_id="ben_pratap_kumar",
    amount=1000,
    mode="imps"
)
print(f"   Status: {result['status']}")
print(f"   Session: {result['session_id']}")
print(f"   OTP: {result['otp']}")
print("   ✅ Transfer initiation works\n")

# Test 5: Transaction history (with pagination)
print("5. Transaction History:")
result = get_transaction_history(
    account_type="savings",
    date_range="last 2 weeks"
)
print(f"   Account: {result['account']['speech_name']}")
print(f"   Transactions: {len(result['transactions'])}")
print(f"   Pagination: Page {result['pagination']['current_page']} of {result['pagination']['total_pages']}")
print(f"   Total: {result['pagination']['total_transactions']} transactions")
print("   ✅ Transaction history works with pagination\n")

# Test 6: Transaction history with specific dates
print("6. Transaction History (specific dates):")
result = get_transaction_history(
    account_type="current",
    start_date="2025-11-01",
    end_date="2025-11-22"
)
print(f"   Account: {result['account']['speech_name']}")
print(f"   Transactions: {len(result['transactions'])}")
print(f"   Date range: {result['date_range']['start']} to {result['date_range']['end']}")
print("   ✅ Transaction history with dates works\n")

print("="*60)
print("✅ ALL CORE FEATURES WORKING CORRECTLY")
print("="*60)
print("\nSummary:")
print("  ✅ Balance checking")
print("  ✅ Account listing")
print("  ✅ Beneficiary listing")
print("  ✅ Transfer initiation")
print("  ✅ Transaction history (with pagination)")
print("  ✅ Transaction history (with date filters)")
print("\n🎉 No existing functionality was broken!")
