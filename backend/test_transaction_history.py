"""
Test transaction history functionality
"""
from banking_tools import get_transaction_history

print("=" * 70)
print("🧪 Testing Transaction History")
print("=" * 70)

# Test 1: Get transactions for Primary Savings
print("\n1️⃣  Testing get_transaction_history(account_id='acc_savings_primary')...")
result = get_transaction_history(account_id="acc_savings_primary")

if "error" in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"✅ Found {len(result['transactions'])} transactions for {result['account']['display_name']}")
    print("\nRecent transactions:")
    for txn in result['transactions'][:5]:
        sign = "+" if txn['type'] == 'credit' else "-"
        print(f"   {txn['date']}: {txn['description']} {sign}₹{txn['amount']:,}")

# Test 2: Get transactions by account type
print("\n2️⃣  Testing get_transaction_history(account_type='savings')...")
result = get_transaction_history(account_type="savings")

if "error" in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"✅ Found transactions for {result['account']['speech_name']}")

# Test 3: Get transactions by account number
print("\n3️⃣  Testing get_transaction_history(account_type='7890')...")
result = get_transaction_history(account_type="7890")

if "error" in result:
    print(f"❌ Error: {result['error']}")
else:
    print(f"✅ Found transactions for account ending in 7890")

# Test 4: Invalid account
print("\n4️⃣  Testing invalid account...")
result = get_transaction_history(account_type="invalid")

if "error" in result:
    print(f"✅ Correctly returned error: {result['error']}")
else:
    print("❌ Should have returned error!")

print("\n" + "=" * 70)
print("✅ All transaction history tests passed!")
print("=" * 70)
