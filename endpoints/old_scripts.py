import requests
import os
import mimetypes
from datetime import datetime

# Employee and Department mapping
EMPLOYEE_DEPT_MAPPING = """
EMP001 Sales DEP001
EMP002 Finance DEP002
EMP003 Human Resources DEP003
EMP004 Research DEP004
EMP005 Information Technology DEP005
"""

# Valid expense categories
VALID_EXPENSE_CATEGORIES = [
    "Travel Expenses",
    "Work Equipment & Supplies",
    "Meals & Entertainment",
    "Internet & Phone Bills",
    "Professional Development",
    "Health & Wellness",
    "Commuting Expenses",
    "Software & Subscriptions",
    "Relocation Assistance",
    "Client"
]

# Configuration
API_URL = "http://localhost:8000/api/expenses/"

# Test cases with different scenarios
TEST_CASES = [
    {
        "employeeId": "EMP001",
        "departmentId": "DEP001",
        "expenseType": "Travel",
        "description": "Flight tickets for client meeting",
        "categories": "Travel Expenses",
        "receipt_path": "receipt_images/travelfinal.jpg"
    },
    {
        "employeeId": "EMP003",
        "departmentId": "DEP003",
        "expenseType": "Work Equipment",
        "description": "Purchase of office supplies",
        "categories": "Work Equipment & Supplies",
        "receipt_path": "receipt_images/work_supplies.png"
    },
    {
        "employeeId": "EMP001",
        "departmentId": "DEP001",
        "expenseType": "Travel",
        "description": "Going to Pune to meet clients",
        "categories": "Travel Expense",
        "receipt_path": "receipt_images/red bus.pdf"
    },
    {
        "employeeId": "EMP003",
        "departmentId": "DEP003",
        "expenseType": "Travel",
        "description": "Going to Pune to meet clients",
        "categories": "Travel Expense",
        "receipt_path": "receipt_images/red bus.pdf"
    },

]

def validate_expense(test_case):
    """Validate expense data before submission"""
    if not test_case["employeeId"] or not test_case["departmentId"]:
        return False, "Employee ID and Department ID are required"
    
    if test_case["categories"] not in VALID_EXPENSE_CATEGORIES:
        return False, f"Invalid expense category. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
    
    if not os.path.exists(test_case["receipt_path"]):
        return False, f"Receipt file not found at {test_case['receipt_path']}"
    
    return True, "Validation successful"

def submit_expense(test_case):
    """Submit a single expense with receipt"""
    # Validate the expense data
    is_valid, message = validate_expense(test_case)
    if not is_valid:
        print(f"Validation Error: {message}")
        return
    
    # Get file content type
    content_type, _ = mimetypes.guess_type(test_case["receipt_path"])
    if not content_type:
        content_type = 'application/pdf'
    
    # Prepare the data payload
    data = {
        "employeeId": test_case["employeeId"],
        "departmentId": test_case["departmentId"],
        "expenseType": test_case["expenseType"],
        "description": test_case["description"],
        "categories": test_case["categories"]
    }
    
    # Print submission details
    print(f"\nSubmitting expense:")
    print(f"Employee: {data['employeeId']}")
    print(f"Department: {data['departmentId']}")
    print(f"Type: {data['expenseType']}")
    print(f"Description: {data['description']}")
    print(f"Category: {data['categories']}")
    print(f"Receipt: {test_case['receipt_path']}")
    
    try:
        with open(test_case["receipt_path"], 'rb') as f:
            files = {
                'receipt': (os.path.basename(test_case["receipt_path"]), f, content_type)
            }
            response = requests.post(API_URL, data=data, files=files)
            
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.json())
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {API_URL}. Please check if the server is running.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def run_all_tests():
    """Run all test cases"""
    print(f"Starting expense submission tests at {datetime.now()}")
    print("=" * 50)
    
    for test_case in TEST_CASES:
        submit_expense(test_case)
        print("=" * 50)

def create_receipt_directories():
    """Create necessary directories for receipts if they don't exist"""
    directories = ["receipt_images"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

if __name__ == "__main__":
    # Create necessary directories
    create_receipt_directories()
    
    # Run the tests
    run_all_tests()