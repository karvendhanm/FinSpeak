import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Security Configuration
MASTER_OTP = "123456"  # Hackathon hack - always works
OTP_REQUIRED_FUNCTIONS = [
    "transfer_money",
    "update_beneficiary",
    "change_limit"
]

# AWS Polly Configuration
POLLY_VOICE_ID = "Kajal"   # Female Indian English voice
POLLY_ENGINE = "neural"    # Better quality

# AWS Transcribe Configuration
TRANSCRIBE_LANGUAGE_CODE = "en-US"
TRANSCRIBE_SAMPLE_RATE = 8000  # 8kHz for speech
