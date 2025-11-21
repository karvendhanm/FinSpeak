import boto3
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def call_bedrock_llm(system_prompt, user_message, model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0"):
    """Call AWS Bedrock Claude model with system prompt and user message"""
    
    messages = [
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    request_body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "system": system_prompt,
        "messages": messages,
        "temperature": 0.0,
    })

    accept = "application/json"
    content_type = "application/json"

    response = bedrock_client.invoke_model(
        body=request_body,
        modelId=model_id,
        accept=accept,
        contentType=content_type,
    )
    
    response_body = json.loads(response['body'].read())
    assistant_message = response_body['content'][0]['text']
    
    print(f"\n=== RAW LLM OUTPUT ===")
    print(assistant_message)
    print(f"=== END RAW OUTPUT ===\n")
    
    return assistant_message

def parse_llm_response(llm_output):
    """Parse LLM response to extract thinking and function call"""
    
    # Extract thinking
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', llm_output, re.DOTALL)
    thinking = thinking_match.group(1).strip() if thinking_match else ""
    
    # Extract response JSON
    response_match = re.search(r'<response>(.*?)</response>', llm_output, re.DOTALL)
    if not response_match:
        return {
            "thinking": thinking,
            "function_name": None,
            "function_params": {}
        }
    
    response_json_str = response_match.group(1).strip()
    
    # Parse JSON
    try:
        response_data = json.loads(response_json_str)
        
        # Handle both formats: function_name or function_call
        function_name = response_data.get("function_name")
        if not function_name and response_data.get("function_call"):
            function_name = response_data["function_call"].get("name")
        
        return {
            "thinking": thinking,
            "function_name": function_name,
            "function_params": response_data.get("function_params", {})
        }
    except json.JSONDecodeError:
        return {
            "thinking": thinking,
            "function_name": None,
            "function_params": {}
        }
