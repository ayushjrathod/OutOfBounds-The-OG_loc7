import requests
import os
import mimetypes
from fastapi import HTTPException

def test_expense_submission(file_path: str):
    # API endpoint
    file_path = "receipt images/dmart 2.jpg"
    url = "http://localhost:8000/api/expenses/"
    
    # Form data
    data = {
        "employeeId": "EMP123",
        "departmentId": "DEP456",
        "expenseType": "client_meeting",
        "description": "client Dolph AI request",
        "vendor": "Restaurant ABC"
    }
    
    # Verify file exists
    if not os.path.exists(file_path):
        print(f"Error: Receipt file not found at {file_path}")
        return
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'image/jpeg'
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
    if not any(content_type.startswith(t) for t in allowed_types):
        print(f"Error: Invalid file type. Supported types: {', '.join(allowed_types)}")
        return
    
    try:
        # Create files dict with receipt and proper content type
        with open(file_path, 'rb') as f:
            files = {
                'receipt': (os.path.basename(file_path), f, content_type)
            }
            
            # Send POST request
            response = requests.post(url, data=data, files=files)
        
        # Print response
        print(f"\nFile type: {content_type}")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    # Get file path from command line or input
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter receipt file path: ")
    test_expense_submission(file_path)
