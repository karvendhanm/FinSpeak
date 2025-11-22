"""
Simple test script for Nidhi fund transfer workflow
"""
import asyncio
import sys
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from banking_tools import FUND_TRANSFER_TOOLS, pending_transfers
from agent_prompt import SYSTEM_PROMPT

load_dotenv()

async def test_fund_transfer():
    """Test the complete fund transfer workflow"""
    
    print("=" * 70)
    print("🏦 NIDHI - Fund Transfer Test")
    print("=" * 70)
    
    # Create agent
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
    
    # Test conversation
    conversation = [
        "Send 5000 rupees to Pratap Kumar",
        # Agent will ask for source account
        "Primary Savings",
        # Agent will confirm and call initiate_transfer
        "Yes, confirm"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n{'─' * 70}")
        print(f"Step {i}: User: {user_input}")
        print(f"{'─' * 70}")
        
        try:
            result = await agent.invoke_async(user_input)
            response = result.content if hasattr(result, 'content') else str(result)
            
            print(f"Nidhi: {response}")
            
            # Check if OTP was generated
            if "OTP" in response:
                print(f"\n{'🔐' * 35}")
                print("OTP GENERATED - Transfer ready for verification!")
                print(f"{'🔐' * 35}")
                
                # Show pending transfers
                if pending_transfers:
                    print(f"\nPending Transfers: {len(pending_transfers)}")
                    for session_id, data in pending_transfers.items():
                        print(f"  Session: {session_id}")
                        print(f"  OTP: {data['otp']}")
                        print(f"  Amount: ₹{data['amount']:,}")
                        print(f"  From: {data['from_account']}")
                        print(f"  To: {data['to_beneficiary']}")
                
                break  # Stop after OTP generation
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print(f"\n{'=' * 70}")
    print("✅ Test completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    print("\n🚀 Starting Nidhi test...\n")
    asyncio.run(test_fund_transfer())
