"""Test pagination functionality"""
from banking_tools import get_transaction_history, next_page, previous_page

print("Testing pagination functionality...\n")

# Test 1: Get first page
print("1. Getting first page of transactions...")
result = get_transaction_history(account_type="savings", date_range="last month")
assert result["pagination"]["current_page"] == 1
assert result["pagination"]["total_pages"] >= 1
session_id = result["pagination"]["session_id"]
print(f"   ✅ Page 1 of {result['pagination']['total_pages']}")
print(f"   Session ID: {session_id}")
print(f"   Showing {len(result['transactions'])} transactions")

# Test 2: Navigate to next page
if result["pagination"]["total_pages"] > 1:
    print("\n2. Navigating to next page...")
    result2 = next_page(session_id)
    assert result2["pagination"]["current_page"] == 2
    print(f"   ✅ Page 2 of {result2['pagination']['total_pages']}")
    print(f"   Showing {len(result2['transactions'])} transactions")
    
    # Test 3: Navigate back to previous page
    print("\n3. Navigating back to previous page...")
    result3 = previous_page(result2["pagination"]["session_id"])
    assert result3["pagination"]["current_page"] == 1
    print(f"   ✅ Back to page 1")
    print(f"   Showing {len(result3['transactions'])} transactions")
    
    # Test 4: Try to go to previous page from page 1 (should error)
    print("\n4. Testing boundary: previous from page 1...")
    result4 = previous_page(result3["pagination"]["session_id"])
    assert "error" in result4
    print(f"   ✅ Correctly prevented: {result4['error']}")
    
    # Test 5: Navigate to last page
    print("\n5. Navigating to last page...")
    last_page = result["pagination"]["total_pages"]
    result5 = get_transaction_history(
        account_type="savings", 
        date_range="last month", 
        page=last_page
    )
    assert result5["pagination"]["current_page"] == last_page
    print(f"   ✅ Page {last_page} of {last_page}")
    
    # Test 6: Try to go to next page from last page (should error)
    print("\n6. Testing boundary: next from last page...")
    result6 = next_page(result5["pagination"]["session_id"])
    assert "error" in result6
    print(f"   ✅ Correctly prevented: {result6['error']}")
else:
    print("\n   ℹ️  Only 1 page of transactions, skipping navigation tests")

# Test 7: Invalid session ID
print("\n7. Testing invalid session ID...")
result7 = next_page("invalid-session-id")
assert "error" in result7
print(f"   ✅ Correctly handled: {result7['error']}")

print("\n✅ All pagination tests passed!")
print("   - Navigation works correctly")
print("   - Boundaries are enforced")
print("   - Session management works")
