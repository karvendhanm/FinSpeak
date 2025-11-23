# FinSpeak Compliance & Privacy Framework

## Regulatory Compliance

### RBI (Reserve Bank of India) Guidelines

#### 1. **Authentication & Authorization**
✅ **Two-Factor Authentication (2FA)**
- OTP-based verification for all fund transfers
- 6-digit OTP with 5-minute expiry
- Master OTP for demo/testing purposes

✅ **Transaction Limits**
- IMPS: Up to ₹5,00,000 per transaction
- NEFT: No upper limit (working hours)
- RTGS: Minimum ₹2,00,000 (working hours)

✅ **Session Management**
- User-specific agent sessions
- Automatic session timeout after inactivity
- Secure session ID generation

#### 2. **Data Security & Privacy**

✅ **PII Protection**
- Account numbers masked in logs (show only last 4 digits)
- Beneficiary details encrypted in transit
- No storage of voice recordings beyond processing

✅ **Audit Trail**
- Complete audit logging of all banking operations
- Timestamp, user ID, action, status tracked
- Immutable audit logs in separate database
- 7-year retention policy (RBI requirement)

✅ **Data Encryption**
- TLS 1.3 for all API communications
- Database encryption at rest (SQLite with encryption extension)
- AWS S3 server-side encryption for temporary audio files
- Immediate deletion of audio files post-transcription

#### 3. **Transaction Monitoring**

✅ **Anomaly Detection**
- High-value transaction alerts (>₹50,000)
- Rapid transfer detection (3+ transfers in 5 minutes)
- New beneficiary verification for amounts >₹25,000
- Real-time risk scoring (LOW/MEDIUM/HIGH)

✅ **Fraud Prevention**
- Balance verification before transfer initiation
- Duplicate transaction prevention
- Same-account transfer blocking
- Beneficiary validation

### GDPR Compliance

#### 1. **Data Minimization**
- Collect only essential banking data
- No unnecessary personal information stored
- Voice data processed and immediately deleted

#### 2. **Right to Access**
- Users can request audit logs via `/api/audit-logs`
- Transaction history available for 3 months
- Account data accessible through balance check

#### 3. **Right to Erasure**
- User data deletion on account closure
- Audio files auto-deleted after transcription
- Session data cleared on logout

#### 4. **Consent Management**
- Explicit consent for voice recording
- Clear privacy policy displayed
- Opt-in for data processing

### IT Act 2000 (India)

✅ **Digital Signatures & Authentication**
- OTP serves as digital authentication
- Non-repudiation through audit logs
- Secure electronic records

✅ **Data Protection**
- Reasonable security practices implemented
- Sensitive personal data protected
- Breach notification procedures defined

## Security Architecture

### 1. **Voice Data Handling**
```
User Voice → Web Speech API/AWS Transcribe → Text Processing → Immediate Deletion
                                                    ↓
                                            No Voice Storage
```

### 2. **Transaction Flow Security**
```
User Request → Authentication → Risk Analysis → OTP Verification → Execution → Audit Log
                     ↓                ↓                ↓                ↓
                 Session ID      Risk Scoring    2FA Required    Encrypted DB
```

### 3. **Data Storage**
- **Encrypted**: Account balances, transaction history, beneficiary details
- **Masked**: Account numbers in logs (XXXX7890)
- **Temporary**: Audio files (deleted within 60 seconds)
- **Immutable**: Audit logs (append-only)

## Privacy Policy Summary

### Data Collection
- **Banking Data**: Account numbers, balances, transaction history
- **Voice Data**: Temporary audio for transcription only
- **Usage Data**: Audit logs for security and compliance

### Data Usage
- **Primary Purpose**: Banking operations (transfers, balance checks)
- **Secondary Purpose**: Fraud detection, compliance reporting
- **No Third-Party Sharing**: Data never sold or shared

### Data Retention
- **Transaction History**: 3 months (user-accessible), 7 years (compliance)
- **Audit Logs**: 7 years (RBI requirement)
- **Voice Recordings**: 0 seconds (immediate deletion)
- **Session Data**: Until logout or 30-minute timeout

### User Rights
- Access transaction history and audit logs
- Request data deletion (subject to legal retention)
- Opt-out of voice features (text-only mode available)
- Withdraw consent at any time

## Incident Response

### Data Breach Protocol
1. **Detection**: Automated monitoring and alerts
2. **Containment**: Immediate system isolation
3. **Assessment**: Impact analysis within 24 hours
4. **Notification**: Users notified within 72 hours (GDPR)
5. **Remediation**: Security patches and user support
6. **Reporting**: RBI notification as per guidelines

### Security Monitoring
- Real-time transaction monitoring
- Anomaly detection alerts
- Failed authentication tracking
- Suspicious activity flagging

## Compliance Certifications (Planned)

- [ ] ISO 27001 (Information Security Management)
- [ ] PCI DSS (Payment Card Industry Data Security)
- [ ] SOC 2 Type II (Security, Availability, Confidentiality)
- [ ] RBI Cybersecurity Framework Compliance

## Regular Audits

- **Internal**: Quarterly security audits
- **External**: Annual third-party penetration testing
- **Compliance**: Bi-annual RBI compliance review
- **Code Review**: Continuous security scanning

## Contact

**Data Protection Officer**: dpo@finspeak.bank  
**Security Team**: security@finspeak.bank  
**Compliance Officer**: compliance@finspeak.bank

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Review Cycle**: Quarterly
