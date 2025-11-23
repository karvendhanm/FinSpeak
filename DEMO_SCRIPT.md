# FinSpeak Hackathon Demo Script

## Setup (Before Demo)
1. Start backend: `cd backend && python server.py`
2. Start frontend: `cd finspeak-frontend && npm run dev`
3. Open dashboard: `backend/dashboard.html` in browser
4. Reset database if needed: `rm finspeak.db finspeak_audit.db && python init_db.py`

## Demo Flow (8-10 minutes)

### **Introduction (30 seconds)**
> "Hi! I'm presenting FinSpeak - a voice-driven conversational banking assistant that makes banking as simple as talking to a friend. Let me show you how it works."

---

### **Scene 1: Balance Check (1 minute)**

**Say**: "What's my account balance?"

**Expected Response**: 
- Shows all 3 accounts with balances
- Total balance displayed
- Natural voice response

**Highlight**:
- ✅ Natural language understanding
- ✅ Voice input/output (AWS Transcribe + Polly)
- ✅ Multi-account support

---

### **Scene 2: Transaction History (1.5 minutes)**

**Say**: "Show me my recent transactions for savings account"

**Expected Response**:
- Lists last 5 transactions
- Shows pagination (page 1 of X)

**Say**: "Next page"

**Expected Response**:
- Shows next 5 transactions

**Highlight**:
- ✅ Date filtering and pagination
- ✅ Context retention (remembers account)
- ✅ Voice-based navigation

---

### **Scene 3: Fund Transfer - Own Account (2 minutes)**

**Say**: "Transfer money"

**Expected Response**: "Transfer to beneficiary or your own account?"

**Say**: "My own account"

**Expected Response**: Shows 3 accounts with balances

**Say**: "Current account"

**Expected Response**: Shows 2 destination accounts (excluding current)

**Say**: "Savings account"

**Expected Response**: "How much would you like to transfer?"

**Say**: "Ten thousand rupees"

**Expected Response**: "Transfer ₹10,000 from Current Account to Savings Account?"

**Say**: "Yes"

**Expected Response**: "An OTP has been sent..."

**Enter OTP**: 123456 (Master OTP)

**Expected Response**: "Transfer successful! ₹10,000 transferred..."

**Highlight**:
- ✅ Multi-turn conversation
- ✅ OTP authentication (2FA)
- ✅ Real-time balance updates
- ✅ Transaction logging

---

### **Scene 4: Loan & Credit Card Inquiry (1 minute)**

**Say**: "What's my loan status?"

**Expected Response**: Shows home loan and personal loan details

**Say**: "Credit card limit?"

**Expected Response**: Shows credit card details with available credit

**Highlight**:
- ✅ Comprehensive banking operations
- ✅ Loan and credit card management

---

### **Scene 5: Payment Reminders (1 minute)**

**Say**: "What payments are due?"

**Expected Response**: Shows upcoming EMIs, bills with due dates

**Highlight**:
- ✅ Proactive financial management
- ✅ Payment tracking

---

### **Scene 6: Observability Dashboard (2 minutes)**

**Switch to dashboard.html**

**Show**:
- Total transactions count
- Success rate percentage
- Total amount transferred
- Recent activity (24h)
- Audit logs with timestamps

**Highlight**:
- ✅ Real-time monitoring
- ✅ Audit trail for compliance
- ✅ Transaction metrics
- ✅ Risk detection (if high-value transfer was made)

**Optional**: Make a high-value transfer (₹60,000) to show risk alert in logs

---

### **Scene 7: Security & Compliance (1 minute)**

**Show documents**:
1. Open `COMPLIANCE.md` - scroll to show:
   - RBI compliance
   - GDPR compliance
   - PII masking
   - Audit trails

2. Open `PILOT_PLAN.md` - scroll to show:
   - ROI: 853% Year 1
   - Cost savings: ₹8.1 Crore annually
   - Phased rollout strategy

**Highlight**:
- ✅ Enterprise-ready security
- ✅ Regulatory compliance
- ✅ Clear business case

---

### **Closing (30 seconds)**

> "FinSpeak delivers:
> - **70% faster transactions** - 5 minutes to 1.5 minutes
> - **60% cost reduction** - ₹8.1 Crore annual savings
> - **24/7 availability** - Voice banking anytime, anywhere
> - **Enterprise security** - OTP, encryption, audit trails, anomaly detection
> - **853% ROI** in Year 1
> 
> All powered by AWS Bedrock (Claude Sonnet 4), Transcribe, and Polly. Thank you!"

---

## Backup Scenarios (If Time Permits)

### **Beneficiary Transfer**
**Say**: "Send 5000 to Pratap Kumar"
- Shows account selection
- Shows beneficiary confirmation
- Shows transfer mode selection (IMPS/NEFT/RTGS)
- OTP verification
- Success confirmation

### **Error Handling**
**Say**: "Transfer 1 million rupees"
- Shows insufficient balance error
- Graceful error recovery

### **Date Range Query**
**Say**: "Show transactions for last 2 weeks"
- Demonstrates date parsing
- Shows filtered results

---

## Key Talking Points

### **Innovation**
- AI-powered conversation (Claude Sonnet 4)
- Natural language understanding
- Context-aware responses
- Multi-turn dialogue management

### **Security**
- Two-factor authentication (OTP)
- Real-time anomaly detection
- PII masking in logs
- Complete audit trails
- Encryption at rest and in transit

### **Business Impact**
- 70% reduction in transaction time
- 60% reduction in operational costs
- 853% ROI in Year 1
- ₹8.1 Crore annual savings
- 24/7 availability

### **Compliance**
- RBI guidelines compliance
- GDPR data protection
- IT Act 2000 compliance
- 7-year audit retention
- Incident response protocols

### **Scalability**
- Cloud-native architecture (AWS)
- Auto-scaling capabilities
- 99.9% uptime SLA
- Handles 1000+ concurrent users

---

## Troubleshooting

### If voice input doesn't work:
- Use text input (type in chat)
- Check microphone permissions
- Refresh page

### If OTP doesn't work:
- Use Master OTP: **123456**
- Check console for generated OTP

### If backend is slow:
- First request may take 5-10 seconds (cold start)
- Subsequent requests are fast (<2 seconds)

### If demo crashes:
- Restart backend: `python server.py`
- Clear browser cache
- Check `backend/finspeak.db` exists

---

## Questions to Anticipate

**Q: How do you handle regional languages?**
A: Currently English, but architecture supports multi-language via AWS Transcribe (Hindi, Tamil, Telugu ready to add).

**Q: What about voice biometrics?**
A: Planned for Phase 2 using AWS speaker verification or SpeechBrain.

**Q: How do you prevent fraud?**
A: Multi-layered: OTP authentication, anomaly detection (high amounts, rapid transfers, new beneficiaries), real-time monitoring, audit trails.

**Q: What's the latency?**
A: <2 seconds for most operations, <5 seconds for voice transcription.

**Q: Can it handle complex queries?**
A: Yes! Claude Sonnet 4 handles ambiguity, multi-turn conversations, and context retention.

**Q: What's the cost per transaction?**
A: ~₹2 per transaction vs ₹150 for branch, ₹50 for call center.

---

**Good luck with your demo! 🚀**
