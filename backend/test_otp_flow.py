"""
Test OTP flow - verify OTP is hidden from user
"""
import asyncio
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from banking_tools import FUND_TRANSFER_TOOLS
from agent_prompt import SYSTEM_PROMPT

load_dotenv()

async def test_otp_hidden():
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-west-2",
        temperature=0,
    )
    
    agent = Agent(
        name='nidhi_test',
        model=bedrock_model,
        system_prompt=SYSTEM_PROMPT,
        tools=FUND_TRANSFER_TOOLS
    )
    
    # Simulate full conversation
    steps = [
        "Send 5000 rupees to Pratap Kumar",
        "Primary Savings",
        "IMPS",
        "Yes"
    ]
    
    for step in steps:
        print(f"\nUser: {step}")
        result = await agent.invoke_async(step)
        response = result.content if hasattr(result, 'content') else str(result)
        print(f"Agent: {response}")
        
        # Check if OTP digits are in response
        import re
        if re.search(r'\b\d{6}\b', response):
            print("\n❌ FAIL: OTP digits found in response!")
            return False
    
    print("\n✅ PASS: OTP not revealed to user")
    return True

if __name__ == "__main__":
    asyncio.run(test_otp_hidden())
