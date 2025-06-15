import os
import sys
import io
import json
import boto3
from datetime import datetime
from pathlib import Path
from typing import List, Dict
# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.aws_utilities import is_aws_environment, read_file_from_s3, save_text_to_s3

def get_timestamp():
    """Get current timestamp in YYYYMMDD_HHMMSS format"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_report_settings(settings):
    try:
        print(f"!!!!!===Inside save_report_settings=Settings: {settings}")
        
        # Ensure settings is a dictionary
        if isinstance(settings, str):
            settings = json.loads(settings)
            
        # Add timestamp as ID
        settings['id'] = get_timestamp()
        
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('report_settings')
        
        # Save to DynamoDB
        response = table.put_item(
            Item=settings
        )
        
        print(f"!!!!!===Save successful, ID: {settings['id']}")
        return ({
            "status": "success",
            "id": settings['id'],
            "message": "Settings saved successfully"
        },None)
        
    except Exception as e:
        error_msg = f"Error saving settings: {str(e)}"
        print(f"!!!!!===Error: {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    test_settings ={
  "title": "Report Title",
  "logo": {
    "url": "",
    "position": "left"
  },
  "data": {
    "headers": [
      "id1111",
      "first_name2222",
      "last_name",
      "salary",
      "department\r"
    ],
    "rows": [
      [
        "1",
        "John",
        "Smith",
        "20000",
        "Reporting\r"
      ],
      [
        "2",
        "Ian",
        "Peterson",
        "80000",
        "Engineering\r"
      ],
      [
        "3",
        "Mike",
        "Peterson",
        "20000",
        "Engineering\r"
      ],
      [
        "4",
        "Cailin",
        "Ninson",
        "30000",
        "Engineering\r"
      ],
      [
        "5",
        "John",
        "Mills",
        "50000",
        "Marketing\r"
      ],
      [
        "6",
        "Ava",
        "Muffinson",
        "10000",
        "Silly Walks\r"
      ]
    ]
  },
  "chart": {
    "type": "line",
    "xAxis": "first_name2222",
    "yAxis": "salary"
  }
}
    result = save_report_settings(test_settings)
    print(f"Test result: {result}")

