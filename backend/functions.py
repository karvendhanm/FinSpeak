# Function Definitions for FinSpeak Banking Assistant
# These are the tools/functions available to the LLM

# Banking workflow functions
banking_functions = {
    "transfer_money_workflow": {
        "name": "transfer_money_workflow",
        "title": "Transfer Money Workflow",
        "func_type": "FUNCTION",
        "description": "Initiate money transfer to a beneficiary. Handles account selection, beneficiary disambiguation, transfer mode selection (IMPS/NEFT/RTGS for inter-bank), and OTP verification. Call this function when user wants to send money, transfer funds, or pay someone. Do NOT ask for parameters - the workflow will collect them step by step.",
        "parameters": {}
    },
    "check_balance_workflow": {
        "name": "check_balance_workflow",
        "title": "Check Balance Workflow",
        "func_type": "FUNCTION",
        "description": "Check account balance. If user has multiple accounts, will ask which account to check. Call this function when user wants to know their balance, check how much money they have, or inquire about account balance. Do NOT ask for parameters - the workflow will handle account selection.",
        "parameters": {}
    },
    "transaction_history_workflow": {
        "name": "transaction_history_workflow",
        "title": "Transaction History Workflow",
        "func_type": "FUNCTION",
        "description": "View transaction history for an account. Supports date range filtering (e.g., 'last 7 days', 'last 3 weeks', 'this month'). Call this function when user wants to see transactions, view statement, or check transaction history. Do NOT ask for parameters - the workflow will collect them.",
        "parameters": {}
    },
    "resume_workflow": {
        "name": "resume_workflow",
        "title": "Resume Workflow",
        "func_type": "FUNCTION",
        "description": "Resume a paused workflow by providing the required input. This function is automatically available when a workflow is in WAITING state and needs user input to proceed. The parameters for this function are dynamically determined based on what the workflow is waiting for.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "cancel_workflow": {
        "name": "cancel_workflow",
        "title": "Cancel Workflow",
        "func_type": "FUNCTION",
        "description": "Cancel the ongoing workflow when user explicitly requests to stop, cancel, or abort the current operation.",
        "parameters": {}
    }
}

def get_function_schema(function_name):
    """Get function schema by name"""
    return banking_functions.get(function_name)

def get_all_functions():
    """Get all available functions"""
    return banking_functions

def format_functions_for_llm():
    """
    Format functions for LLM consumption in <tools> section
    Returns formatted string with function definitions
    """
    formatted = []
    for func_name, func_def in banking_functions.items():
        func_str = f"""
<tool>
  <name>{func_def['name']}</name>
  <description>{func_def['description']}</description>
  <parameters>{func_def.get('parameters', {})}</parameters>
</tool>"""
        formatted.append(func_str)
    
    return "\n".join(formatted)

def get_available_functions_for_state(workflow_state=None):
    """
    Get available functions based on workflow state
    
    Args:
        workflow_state: Current workflow state (None, "WAITING", "RUNNING", etc.)
    
    Returns:
        List of function names available in current state
    """
    base_functions = [
        "transfer_money_workflow",
        "check_balance_workflow",
        "transaction_history_workflow"
    ]
    
    if workflow_state == "WAITING":
        # Add resume_workflow when waiting for input
        return base_functions + ["resume_workflow", "cancel_workflow"]
    elif workflow_state == "RUNNING":
        # Add cancel_workflow when workflow is running
        return base_functions + ["cancel_workflow"]
    else:
        # Default: only base workflows
        return base_functions
