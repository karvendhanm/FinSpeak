# FinSpeak Comprehensive Test Suite

## Test 1: Balance Check (All Accounts)

### Input:
```
What's my balance?
```

### Expected Behavior:
**UI:**
- Shows text response with all 3 accounts
- Displays total balance: ₹34,86,600
- Lists:
  - Savings Account ending with 7890: ₹10,00,000
  - Current Account ending with 3456: ₹23,86,600
  - Savings Account ending with 6789: ₹1,00,000
- Kajal voice reads the response

**Backend Terminal:**
- Shows: "User: What's my balance?"
- Shows: "Agent: [response with balances]"

**Dashboard:**
- No new entries (read-only operation)

---

## Test 2: Balance Check (Specific Account)

### Input:
```
What's my savings account balance?
```

### Expected Behavior:
**UI:**
- Shows only savings accounts
- Displays balances for accounts ending with 7890 and 6789
- Kajal voice reads the response

**Backend Terminal:**
- Shows filtered account query

**Dashboard:**
- No new entries

---

## Test 3: Transaction History

### Input:
```
Show my recent transactions
```

### Expected Behavior:
**UI:**
- Agent asks: "Which account?"
- Shows clickable buttons:
  - Savings Account (XXXX7890)
  - Current Account (XXXX3456)
  - Savings Account (XXXX6789)

**Next Step:** Click on "Savings Account (XXXX7890)"

### Expected After Click:
**UI:**
- Shows 5 transactions in colored boxes:
  - Green boxes for credits (+₹)
  - Red boxes for debits (-₹)
- Each shows: Date, Description, Amount
- Pagination info if more than 5 transactions

**Backend Terminal:**
- Shows: "📊 Detected X transactions"
- Shows: "📤 Sending X transactions"

**Dashboard:**
- No new entries (read-only)

---

## Test 4: Own Account Transfer (Full Flow)

### Input:
```
Transfer 5000 to my savings account
```

### Expected Behavior:

**Step 1 - Transfer Type:**
- Agent asks: "Are you sending money to a registered beneficiary or to one of your own accounts?"
- Shows 2 buttons:
  - To a registered beneficiary
  - To my own account

**Action:** Click "To my own account"

**Step 2 - Source Account:**
- Shows source account options (3 accounts)
- Each as clickable button

**Action:** Click "Current Account (XXXX3456)"

**Step 3 - Destination Account:**
- Shows destination accounts (excludes Current Account)
- Shows 2 options:
  - Savings Account (XXXX7890)
  - Savings Account (XXXX6789)

**Action:** Click "Savings Account (XXXX7890)"

**Step 4 - Confirmation:**
- Shows confirmation summary box:
  - Amount: ₹5,000
  - From: Current Account ending with 3456
  - To: Savings Account ending with 7890
- Shows 2 buttons:
  - ✓ Yes, Confirm
  - ✕ No, Cancel

**Action:** Click "✓ Yes, Confirm"

**Step 5 - OTP:**
- Shows OTP input modal with 6 boxes
- Message: "An OTP has been sent to your registered mobile number"

**Backend Terminal:**
- Shows: "🔐 OTP GENERATED: XXXXXX"
- Shows: "Master OTP: 123456"
- Shows: "Session ID: txn_XXXXX"

**Action:** Enter OTP: `123456`

**Step 6 - Success:**
- Shows green success modal with checkmark
- Message: "Transfer successful! 5,000 rupees transferred..."
- Shows Transaction ID: TXNYYYYMMDDHHMMSSXXXX
- Celebration animation

**Backend Terminal:**
- Shows: "✅ OTP verified!"
- Shows: "💰 Own account transfer executed!"
- Shows: "Transaction ID: TXNXXXXXX"
- Shows new balances

**Dashboard:**
- Open `backend/dashboard.html` in browser
- Should show:
  - Total transactions increased by 1
  - Success rate: 100%
  - Total amount transferred increased by ₹5,000
  - Recent activity shows new transfer

---

## Test 5: Beneficiary Transfer

### Input:
```
Send 2000 to Pratap Kumar
```

### Expected Behavior:

**Step 1 - Transfer Type:**
- Agent asks about transfer type
- Shows 2 buttons

**Action:** Click "To a registered beneficiary"

**Step 2 - Source Account:**
- Shows 3 account options

**Action:** Click "Savings Account (XXXX7890)"

**Step 3 - Beneficiary Selection:**
- Shows beneficiary list:
  - Pratap Kumar
  - Ananya Sharma
  - Rajesh Patel

**Action:** Click "Pratap Kumar"

**Step 4 - Transfer Mode:**
- Shows 3 mode options:
  - IMPS - Instant (24x7)
  - NEFT - Within 2 working hours
  - RTGS - Real-time (₹2 lakh+, only in working hours)

**Action:** Click "IMPS"

**Step 5 - Confirmation:**
- Shows summary:
  - Amount: ₹2,000
  - From: Savings Account ending with 7890
  - To: Pratap Kumar
  - Mode: IMPS

**Action:** Click "✓ Yes, Confirm"

**Step 6 - OTP & Success:**
- Same as Test 4

**Backend Terminal:**
- Shows OTP generation
- Shows transfer execution
- Shows transaction ID

**Dashboard:**
- Total transactions +1
- Amount transferred +₹2,000

---

## Test 6: Loan Inquiry

### Input:
```
Show me my loans
```

### Expected Behavior:
**UI:**
- Shows 2 purple gradient boxes:

**Box 1 - Home Loan:**
- Outstanding: ₹25,00,000
- EMI: ₹25,000
- Due Date: 5th of every month
- Interest Rate: 8.5%
- Remaining Tenure: 15 years remaining

**Box 2 - Personal Loan:**
- Outstanding: ₹1,50,000
- EMI: ₹5,000
- Due Date: 10th of every month
- Interest Rate: 12%
- Remaining Tenure: 2 years 6 months remaining

**Backend Terminal:**
- Shows: "🏦 Detected 2 loans"
- Shows: "📤 Sending 2 loans"

**Dashboard:**
- No new entries (read-only)

---

## Test 7: Credit Card Inquiry

### Input:
```
What's my credit card status?
```

### Expected Behavior:
**UI:**
- Shows 1 blue gradient box:

**Grace Hopper Platinum Card (****5678):**
- Available Credit: ₹4,55,000
- Credit Limit: ₹5,00,000
- Total Due: ₹45,000
- Minimum Due: ₹2,250
- Payment Due On: 15th

**Backend Terminal:**
- Shows: "💳 Detected 1 credit cards"
- Shows: "📤 Sending 1 credit cards"

**Dashboard:**
- No new entries (read-only)

---

## Test 8: Payment Reminders

### Input:
```
Show upcoming payments
```

### Expected Behavior:
**UI:**
- Shows 4 orange gradient boxes with countdown:
  1. Home Loan EMI - ₹25,000 - Due on 5th December (X days left)
  2. Personal Loan EMI - ₹5,000 - Due on 10th December (X days left)
  3. Credit Card Payment - ₹2,250 - Due on 15th December (X days left)
  4. Electricity Bill - ₹850 - Due on 1st December (X days left)

**Backend Terminal:**
- Shows: "📅 Detected 4 upcoming payments"
- Shows: "📤 Sending 4 payments"

**Dashboard:**
- No new entries (read-only)

---

## Test 9: Hindi Language Support

### Input:
```
नमस्ते
```

### Expected Behavior:
**UI:**
- Shows greeting response
- **Aditi voice** (Hindi) speaks (different from Kajal)

**Backend Terminal:**
- Shows: "🗣️ Detected language: hi"
- Shows: "🔊 Using Hindi voice (Aditi)"

**Dashboard:**
- No new entries

---

## Test 10: Error Handling - Insufficient Balance

### Input:
```
Transfer 50000000 to my savings
```

### Expected Behavior:
**UI:**
- After selecting accounts and confirming
- Shows error message: "Insufficient balance. Available: ₹XX,XX,XXX rupees"
- Red error styling

**Backend Terminal:**
- Shows: "❌ Transfer failed: Insufficient balance"

**Dashboard:**
- No new transaction (failed before OTP)

---

## Test 11: Transaction History with Date Filter

### Input:
```
Show transactions from last month
```

### Expected Behavior:
**UI:**
- Agent asks: "Which account?"
- After selection, shows transactions from last 30 days
- Shows pagination if more than 5 transactions

**Backend Terminal:**
- Shows: "📊 Detected X transactions"
- Shows date range used

**Dashboard:**
- No new entries

---

## Test 12: Risk Monitoring (High Value Transfer)

### Input:
```
Transfer 60000 to Pratap Kumar
```

### Expected Behavior:
**Backend Terminal:**
- After OTP generation, shows:
  - "⚠️ RISK ALERT: HIGH risk detected"
  - "- High-value transaction: ₹60,000"
- Transfer still proceeds (just flagged)

**Dashboard:**
- After completion, check audit logs
- Should show risk_alert entry

---

## Dashboard Verification

### Open Dashboard:
```bash
# Open in browser
open backend/dashboard.html
```

### Expected Metrics:
- **Total Transactions:** Should increase with each transfer
- **Success Rate:** Should be 100% (or show failures)
- **Total Amount Transferred:** Sum of all successful transfers
- **Recent Activity (24h):** Shows all actions

### Audit Logs Section:
- Shows all actions with timestamps
- Shows transfer_initiated, otp_verification, transfer_completed
- Shows risk_alert for high-value transfers
- Account numbers are masked (***XXXX)

---

## Test Checklist

- [ ] Test 1: Balance Check (All)
- [ ] Test 2: Balance Check (Specific)
- [ ] Test 3: Transaction History
- [ ] Test 4: Own Account Transfer
- [ ] Test 5: Beneficiary Transfer
- [ ] Test 6: Loan Inquiry
- [ ] Test 7: Credit Card Inquiry
- [ ] Test 8: Payment Reminders
- [ ] Test 9: Hindi Language
- [ ] Test 10: Error Handling
- [ ] Test 11: Date Filter
- [ ] Test 12: Risk Monitoring
- [ ] Dashboard Verification

---

**Start with Test 1 and let me know the result!**
