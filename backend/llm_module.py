def process_user_input(text):
    """
    LLM module that processes user input and decides which function to call.
    Returns: {"content": str, "function": str, "params": dict}
    - content: What LLM says to the user
    - function: Which function to call
    - params: Parameters for the function
    Note: Does NOT decide OTP requirement - that's backend's job for security
    """
    text_lower = text.lower()
    
    # Dummy logic based on keywords - LLM identifies intent and generates response
    if 'transfer' in text_lower or 'send' in text_lower:
        return {
            "content": "I understand you want to transfer money. Let me help you with that.",
            "function": "transfer_money",
            "params": {"text": text}
        }
    
    elif 'balance' in text_lower or 'account' in text_lower:
        return {
            "content": "Let me check your account balance for you.",
            "function": "get_balance",
            "params": {}
        }
    
    elif 'transaction' in text_lower or 'history' in text_lower:
        return {
            "content": "I'll fetch your recent transaction history.",
            "function": "get_transactions",
            "params": {}
        }
    
    elif 'hello' in text_lower or 'hi' in text_lower:
        return {
            "content": "Hello! I'm your banking assistant. How can I help you today?",
            "function": "greet",
            "params": {}
        }
    
    else:
        return {
            "content": f"I received your message: '{text}'. How can I assist you with your banking needs?",
            "function": "general_query",
            "params": {"text": text}
        }
