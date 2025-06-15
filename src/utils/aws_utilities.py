import boto3
from datetime import datetime
import requests
import os

def get_s3_client(region_name="us-east-1"):
    """Get S3 client"""
    return boto3.client("s3", region_name=region_name)

def get_bedrock_client(region_name="us-east-1"):
    """Get Bedrock client"""
    return boto3.client("bedrock-runtime", region_name=region_name)

def get_textract_client(region_name="us-east-1"):
    """Get Textract client"""
    return boto3.client("textract", region_name=region_name)

def get_timestamp():
    """Get current timestamp in YYYYMMDD_HHMMSS format"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_text_to_s3(text, bucket, key_prefix="text/result_", timestamp=None):
    """
    Save text content to S3 with timestamp
    
    Args:
        text (str): Text content to save
        bucket (str): S3 bucket name
        key_prefix (str): Prefix for the S3 key
        timestamp (str, optional): Timestamp to use. If None, current timestamp will be used
    
    Returns:
        str: The full S3 path where the file was saved
    """
    if timestamp is None:
        timestamp = get_timestamp()
    
    s3 = get_s3_client()
    destination_key = f"{key_prefix}{timestamp}.txt"
    
    s3.put_object(
        Bucket=bucket,
        Key=destination_key,
        Body=text.encode('utf-8')
    )
    
    return f"s3://{bucket}/{destination_key}"

def read_file_from_s3(bucket, key):
    """
    Read file content from S3
    
    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
    
    Returns:
        bytes: File content
    """
    s3 = get_s3_client()
    response = s3.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()

def is_aws_environment():
    """
    Check if the code is running in AWS cloud environment (Lambda, EC2, ECR, etc.)
    
    Returns:
        bool: True if running in AWS cloud, False if running locally
    """
    # Check for Lambda environment
    if os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        return True
        
    # Check for other AWS environments
    aws_env_vars = [
        'AWS_EXECUTION_ENV',  # Present in Lambda, ECS, etc.
        'ECS_CONTAINER_METADATA_URI',  # Present in ECS
        'KUBERNETES_SERVICE_HOST',  # Present in EKS
        'AWS_CONTAINER_CREDENTIALS_RELATIVE_URI'  # Present in ECS, EKS
    ]
    
    # If any of these environment variables exist, we're in AWS
    if any(os.getenv(var) for var in aws_env_vars):
        return True
        
    # Try to get instance metadata as a fallback
    try:
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
