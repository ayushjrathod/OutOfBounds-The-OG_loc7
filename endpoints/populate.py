import requests
import os
import mimetypes
from datetime import datetime

DICT="""
EMP001 Sales DEP001
EMP002 Finance DEP002
EMP003 Human Resources DEP003
EMP004 Research DEP004
EMP005 Information Technology DEP005
"""
# Configuration
API_URL = "http://localhost:8000/api/expenses/"
RECEIPT_PATH = "receipt images/gst-bill-of-supply.jpg"

# Test cases with only required manual inputs
TEST_CASES = [
    
    {
        "employeeId": "EMP004",
        "departmentId": "DEP004",
        "expenseType": "Electrical Suppliances",
        "description": "replacing broken leds",
        "categories": "Work Equipment & Supplies"
    }
]

def submit_expense(test_case):
    """Submit a single expense with minimal required inputs"""
    if not os.path.exists(RECEIPT_PATH):
        print(f"Error: Receipt file not found at {RECEIPT_PATH}")
        return
    
    # Get file content type
    content_type, _ = mimetypes.guess_type(RECEIPT_PATH)
    if not content_type:
        content_type = 'application/pdf'
    
    # Only include required fields
    data = {
        "employeeId": test_case["employeeId"],
        "departmentId": test_case["departmentId"],
        "expenseType": test_case["expenseType"],
        "description": test_case["description"],
        "categories": test_case["categories"]
    }
    
    print(f"\nSubmitting expense:")
    print(f"Employee: {data['employeeId']}")
    print(f"Department: {data['departmentId']}")
    print(f"Type: {data['expenseType']}")
    print(f"Description: {data['description']}")
    
    try:
        with open(RECEIPT_PATH, 'rb') as f:
            files = {
                'receipt': (os.path.basename(RECEIPT_PATH), f, content_type)
            }
            response = requests.post(API_URL, data=data, files=files)
            
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.json())
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def run_all_tests():
    """Run all test cases"""
    print(f"Starting expense submission tests at {datetime.now()}")
    print(f"Using receipt file: {RECEIPT_PATH}")
    print("=" * 50)
    
    for test_case in TEST_CASES:
        submit_expense(test_case)
        print("=" * 50)

if __name__ == "__main__":
    run_all_tests()
