import requests
import boto3
import os
from datetime import datetime
# from constant import (S3_BUCKET_NAME,S3_PDF_PREFIX,DATA_DIR,PDF_CONTENT_TYPE,TIMESTAMP_FORMAT,TEST_PDF_URL)
from src.constant import (
    S3_BUCKET_NAME,
    S3_PDF_PREFIX,
    DATA_DIR,
    PDF_CONTENT_TYPE,
    TIMESTAMP_FORMAT,
    TEST_PDF_URL
)

def download_pdf(url):
    """
    Download PDF from URL
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content

def upload_to_s3(pdf_content):
    """
    Upload PDF content to S3
    """
    try:
        s3_client = boto3.client('s3')
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        s3_key = f"{S3_PDF_PREFIX}{timestamp}.pdf"
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=pdf_content,
            ContentType=PDF_CONTENT_TYPE
        )
        
        return s3_key
    except Exception as e:
        raise Exception(f"Error uploading to S3: {str(e)}")

def save_to_local(pdf_content):
    """
    Save PDF to local /data/ directory
    """
    try:
        # Create /data/ directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        filename = f"{timestamp}.pdf"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_content)
            
        return filepath
    except Exception as e:
        raise Exception(f"Error saving to local: {str(e)}")

def main(url, is_local_test=False):
    """
    Main function to download PDF and upload to S3 or save locally
    
    Args:
        url (str): URL of the PDF file
        is_local_test (bool): If True, save to local directory instead of S3
    """
    try:
        # Download PDF
        pdf_content = download_pdf(url)
        
        if is_local_test:
            # Save to local directory
            filename = save_to_local(pdf_content)
            return filename, None
        else:
            # Upload to S3
            s3_key = upload_to_s3(pdf_content)
            return s3_key, None
            
    except Exception as e:
        return None, str(e)

if __name__ == '__main__':
    # Example usage for local testing
    result, error = main(TEST_PDF_URL, is_local_test=True)
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"PDF saved to: {result}")


