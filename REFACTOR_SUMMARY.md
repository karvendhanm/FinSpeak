# FinSpeak Architecture Refactor Summary

## Changes Made

### 1. **sops.py** - Restructured SOP Architecture
- **Base SOP**: Routes to sub-SOPs using load functions
  - Contains `load_transfer_money_sop`, `load_check_balance_sop`, `load_transaction_history_sop`
  - No workflow tools in base SOP
- **Sub-SOPs**: Each has agent metadata and detailed steps
  - `transfer_money_sop`: Collects amount, beneficiary_name, from_account
  - `check_balance_sop`: Collects account_id
  - `transaction_history_sop`: Collects account_id, time_period
- **SOP_MAPPING**: Maps load functions to sub-SOPs

### 2. **functions.py** - Separated Function Types
- **Load SOP Functions**: Used in base SOP (empty parameters)
  - `load_transfer_money_sop`
  - `load_check_balance_sop`
  - `load_transaction_history_sop`
- **Workflow Functions**: Used in sub-SOPs (full parameter schemas)
  - `transfer_money_workflow`: Requires amount, beneficiary_name, from_account
  - `check_balance_workflow`: Requires account_id
  - `transaction_history_workflow`: Requires account_id, time_period
- **Utility Functions**: resume_workflow, cancel_workflow

### 3. **workflows.py** - Simplified Execution
- Removed complex multi-turn state management
- Workflows now accept parameters directly from LLM
- No session-based parameter collection
- Clean execution with all required parameters

### 4. **server.py** - SOP Context Switching
- Tracks `current_sop` in session (base or sub-SOP name)
- **Base SOP Mode**: Shows load functions only
- **Sub-SOP Mode**: Shows workflow functions with full schemas
- When LLM calls `load_X_sop()`:
  - Switches session to that sub-SOP
  - Next request uses sub-SOP system prompt with workflow functions
- When workflow completes: Resets to base SOP

### 5. **llm_handler.py** - Conversation History
- Added `conversation_history` parameter
- Appends history to system prompt under "Below is the conversation:"
- Maintains conversation context across turns

## Flow Example: Transfer Money

### Turn 1 (Base SOP)
```
User: "Send 5000 to Pratap"
System Prompt: Base SOP + load functions
LLM: Calls load_transfer_money_sop()
Response: "Let me help you with that. What information do you have?"
Session: current_sop = "load_transfer_money_sop"
```

### Turn 2 (Sub-SOP)
```
User: "From my primary savings"
System Prompt: Transfer Money SOP + transfer_money_workflow function with parameters
LLM: Collects amount=5000, beneficiary_name="Pratap", from_account="acc_1"
LLM: Calls transfer_money_workflow(amount=5000, beneficiary_name="Pratap", from_account="acc_1")
Response: "Transfer ready. Please confirm with OTP."
Session: Stores OTP and workflow_params
```

### Turn 3 (OTP Verification)
```
User: Enters OTP
Backend: Verifies OTP
Backend: Executes transfer_money_workflow with stored params
Response: "Transfer successful! $5000 sent to Pratap Kumar..."
Session: current_sop = "base" (reset)
```

## Key Benefits

1. **LLM-Driven Conversation**: LLM naturally collects parameters using function schemas
2. **Clean Separation**: Base SOP routes, sub-SOPs collect, workflows execute
3. **No Complex State**: Workflows are stateless, accept all params at once
4. **Flexible**: Easy to add new workflows by adding sub-SOP + function schema
5. **Production Pattern**: Follows Amazon Sapien architecture

## Files Modified

- `backend/sops.py` - Complete rewrite
- `backend/functions.py` - Complete rewrite
- `backend/workflows.py` - Simplified to parameter-based execution
- `backend/server.py` - Added SOP context switching logic
- `backend/llm_handler.py` - Added conversation history support

## Testing Needed

1. Test base SOP routing to correct sub-SOPs
2. Test parameter collection in sub-SOPs
3. Test workflow execution with collected parameters
4. Test OTP flow for transfers
5. Test conversation history persistence
6. Test reset to base SOP after workflow completion
