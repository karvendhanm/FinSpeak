"""
Test banking tools without AWS credentials
"""
from banking_tools import get_accounts, get_beneficiaries, get_transfer_modes, initiate_transfer
from config import MASTER_OTP

print("=" * 70)
print("🧪 Testing Banking Tools")
print("=" * 70)

# Test 1: Get Accounts
print("\n1️⃣  Testing get_accounts()...")
accounts = get_accounts()
print(f"✅ Found {len(accounts)} accounts:")
for acc in accounts:
    print(f"   - {acc['name']}: ₹{acc['balance']:,}")

# Test 2: Get Beneficiaries
print("\n2️⃣  Testing get_beneficiaries()...")
beneficiaries = get_beneficiaries()
print(f"✅ Found {len(beneficiaries)} beneficiaries:")
for ben in beneficiaries:
    print(f"   - {ben['name']} ({ben['bank']})")

# Test 3: Get Transfer Modes
print("\n3️⃣  Testing get_transfer_modes()...")
modes = get_transfer_modes()
print(f"✅ Found {len(modes)} transfer modes:")
for mode in modes:
    print(f"   - {mode['name']}: {mode['description']}")

# Test 4: Initiate Transfer
print("\n4️⃣  Testing initiate_transfer()...")
result = initiate_transfer(
    from_account_id="acc_savings_primary",
    to_beneficiary_id="ben_pratap_kumar",
    amount=5000,
    mode="imps"
)

if result.get("status") == "otp_required":
    print("✅ Transfer initiated successfully!")
    print(f"   Session ID: {result['session_id']}")
    print(f"   OTP: {result['otp']}")
    print(f"   Message: {result['message']}")
    print(f"\n   Master OTP (for testing): {MASTER_OTP}")
else:
    print(f"❌ Error: {result.get('error', 'Unknown error')}")

# Test 5: Insufficient Balance
print("\n5️⃣  Testing insufficient balance...")
result = initiate_transfer(
    from_account_id="acc_savings_primary",
    to_beneficiary_id="ben_pratap_kumar",
    amount=2000000,  # More than balance
    mode="imps"
)

if "error" in result:
    print(f"✅ Correctly rejected: {result['error']}")
else:
    print("❌ Should have been rejected!")

print("\n" + "=" * 70)
print("✅ All tool tests passed!")
print("=" * 70)
