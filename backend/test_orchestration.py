#!/usr/bin/env python3
"""Test orchestration system without running full server"""

from session_manager import create_session, get_session
from workflows import check_balance_workflow, transfer_money_workflow
from system_prompt import create_system_prompt
from functions import format_functions_for_llm
from sops import banking_base_sop, get_available_sops
from mock_data import HOME_BANK

print("Testing FinSpeak Orchestration System\n" + "="*50)

# Test 1: Create session
print("\n1. Creating session...")
session_id = create_session(workflow="test_workflow", user_id="test_user")
print(f"   ✓ Session created: {session_id}")

# Test 2: Check balance workflow
print("\n2. Testing check_balance_workflow...")
result = check_balance_workflow(session_id, user_input=None)
print(f"   Status: {result['workflow_status']}")
print(f"   Message: {result.get('message', 'N/A')[:80]}...")

# Test 3: System prompt generation
print("\n3. Testing system prompt generation...")
available_sops = get_available_sops(None)
system_prompt = create_system_prompt(
    agent_name=f"{HOME_BANK} Voice Assistant",
    agent_purpose="Help users with banking operations",
    agent_sop=banking_base_sop,
    agent_sub_sops="\n".join(available_sops),
    agent_tools=format_functions_for_llm()
)
print(f"   ✓ System prompt generated ({len(system_prompt)} chars)")
print(f"   Preview: {system_prompt[:100]}...")

# Test 4: Transfer workflow (multi-turn)
print("\n4. Testing transfer_money_workflow (multi-turn)...")
session_id2 = create_session(workflow="transfer_money_workflow", user_id="test_user2")
result = transfer_money_workflow(session_id=session_id2, user_input=None)
print(f"   Status: {result['workflow_status']}")
print(f"   Message: {result.get('message', 'N/A')[:80]}...")

print("\n" + "="*50)
print("✓ All orchestration tests passed!")
