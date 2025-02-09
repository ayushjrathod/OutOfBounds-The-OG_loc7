import requests
import os
import mimetypes
from datetime import datetime
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Update Cloudinary Configuration with correct credentials     
cloudinary.config( 
    cloud_name = os.getenv('cn_cloud_name', 'cnserver'),
    api_key = os.getenv('cn_api_key', '573366814242178'),
    api_secret = os.getenv('cn_api_secret', 'jrrWLurjYfZd9xp0G3UEFYO5kyg'),
    secure = True
)

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
    "Client & Marketing Expenses"
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
        "receipt_path": "receipt images/travelfinal.jpg"
    },
    {
        "employeeId": "EMP002",
        "departmentId": "DEP002",
        "expenseType": "Work Equipment",
        "description": "Purchase of office supplies",
        "categories": "Work Equipment & Supplies",
        "receipt_path": "receipt images/work_supplies.png"
    },
    {
        "employeeId": "EMP003",
        "departmentId": "DEP003",
        "expenseType": "Client Snacks",
        "description": "Nvidia Employees came, had to arrange snacks",
        "categories": "Client & Marketing Expenses",
        "receipt_path": "receipt images/dmart 2.png"
    },
    {
        "employeeId": "EMP005",
        "departmentId": "DEP005",
        "expenseType": "Travel",
        "description": "Travel Bus tickets for client meeting",
        "categories": "Travel Expenses",
        "receipt_path": "receipt images/red bus.pdf"
    },
    {
        "employeeId": "EMP004",
        "departmentId": "DEP004",
        "expenseType": "Work Equipment",
        "description": "Purchase of a high-performance GPU for running deepseek Model",
        "categories": "Work Equipment & Supplies",
        "receipt_path": "receipt images/gpu2.png"
    },
     {
        "employeeId": "EMP004",
        "departmentId": "DEP004",
        "expenseType": "Remote Work Setup",
        "description": "Reimbursement for research staff's work-from-home setup",
        "categories": "Work Equipment & Supplies",
        "receipt_path": "receipt images/workfromhome.jpg"
    },
    {
        "employeeId": "EMP005",
        "departmentId": "DEP005",
        "expenseType": "Software Subscription",
        "description": "Annual cloud computing service subscription",
        "categories": "Software & Subscriptions",
        "receipt_path":"receipt images/software2.png"
    },
    {
        "employeeId": "EMP003",
        "departmentId": "DEP003",
        "expenseType": "Professional Development",
        "description": "Technical training fee",
        "categories": "Professional Development",
        "receipt_path": "receipt images/development.png"
    },
    {
        "employeeId": "EMP002",
        "departmentId": "DEP002",
        "expenseType": "Team Dinner",
        "description": "Dinner with finance department to discuss annual budgeting",
        "categories": "Meals & Entertainment",
        "receipt_path": "receipt images/Hotel-Bill-Sample-and-Format-2.png"
    },
    {
        "employeeId": "EMP001",
        "departmentId": "DEP001",
        "expenseType": "Taxi",
        "description": "Cab fare for client site visit",
        "categories": "Commuting Expenses",
        "receipt_path": "receipt images/cab.jpg"
    },
  {
        "employeeId": "EMP002",
        "departmentId": "DEP002",
        "expenseType": "Office Printer",
        "description": "New high-speed printer for finance department",
        "categories": "Work Equipment & Supplies",
        "receipt_path": "receipt images/invoice_printed.gif"
    },
    {
        "employeeId": "EMP005",
        "departmentId": "DEP005",
        "expenseType": "Hotel Stay",
        "description": "Hotel accommodation for business trip to Banglore IT Hub",
        "categories": "Travel Expenses",
        "receipt_path": "receipt images/hotel_accomodation.png"
    },
    {
        "employeeId": "EMP004",
        "departmentId": "DEP004",
        "expenseType": "Conference Attendance",
        "description": "Tickets for annual financial summit",
        "categories": "Professional Development",
        "receipt_path": "receipt images/conference.png"
    },
     {
        "employeeId": "EMP001",
        "departmentId": "DEP001",
        "expenseType": "Branded Merchandise",
        "description": "Custom-branded pens and notebooks for sales promotions",
        "categories": "Client & Marketing Expendituren",
        "receipt_path": "receipt images/book_pen.png"
    },
    {
        "employeeId": "EMP001",
        "departmentId": "DEP001",
        "expenseType": "Petrol Expense",
        "description": "petrol Travelling to client site",
        "categories": "Travel Expenses",
        "receipt_path": "receipt images/petrol.png"
    },
    {
        "employeeId": "EMP003",
        "departmentId": "DEP003",
        "expenseType": "Dominos",
        "description": "Late Night work by employees on Friday",
        "categories": "Meals & Entertainment",
        "receipt_path": "receipt images/dominos.png"
    }
]

def validate_expense(test_case):
    """Validate expense data before submission"""
    if not test_case["employeeId"] or not test_case["departmentId"]:
        return False, "Employee ID and Department ID are required"
    
    if test_case["categories"] not in VALID_EXPENSE_CATEGORIES:
        return False, f"Invalid expense category. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
    
    if not os.path.exists(test_case["receipt_path"]):
        print(test_case["receipt_path"])
        return False, f"Receipt file not found at {test_case['receipt_path']}"
    
    return True, "Validation successful"

def upload_to_cloudinary(file_path: str) -> str:
    """Upload file to Cloudinary and return secure URL"""
    try:
        print(f"Uploading file: {file_path}")
        # Upload the file with preset and updated parameters
        upload_result = cloudinary.uploader.upload(
            file_path,
            folder="expense_receipts",
            use_filename=True,
            unique_filename=True,
            resource_type="auto",
            upload_preset=os.getenv('NEXT_PUBLIC_CLOUD_UPLOAD_PRESET', 'test_preset'),
            api_key=os.getenv('cn_api_key'),
            api_secret=os.getenv('cn_api_secret')
        )
        
        print(f"Upload successful. Public ID: {upload_result['public_id']}")
        return upload_result['secure_url']
    except Exception as e:
        print(f"Cloudinary upload error details: {str(e)}")
        print(f"Current configuration: {cloudinary.config().cloud_name}")
        raise

def submit_expense(test_case):
    """Submit a single expense with receipt"""
    # Validate the expense data
    is_valid, message = validate_expense(test_case)
    if not is_valid:
        print(f"Validation Error: {message}")
        return
    
    try:
        # Upload receipt to Cloudinary first
        receipt_url = upload_to_cloudinary(test_case["receipt_path"])
        print(f"Receipt uploaded to Cloudinary: {receipt_url}")
        
        # Prepare the form-data with Cloudinary URL
        form_data = {
            "employeeId": test_case["employeeId"],
            "departmentId": test_case["departmentId"],
            "expenseType": test_case["expenseType"],
            "description": test_case["description"],
            "categories": test_case["categories"],
            "receiptImage": receipt_url,  # Send Cloudinary URL
            "vendor": None  # Add vendor if needed
        }
        
        # Print submission details
        print("\nSubmitting expense with data:")
        for key, value in form_data.items():
            print(f"{key}: {value}")
        
        # Send request to API using form-data
        response = requests.post(
            API_URL,
            data=form_data,  # Use form_data instead of JSON
            timeout=30  # Add timeout to prevent hanging
        )
        
        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            print("Success:", response.json())
        else:
            print("Error:", response.json())
            print("Request data:", form_data)  # Print request data for debugging
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {API_URL}. Please check if the server is running.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Request data that failed: {form_data}")  # Print failed request data

def run_all_tests():
    """Run all test cases"""
    print(f"Starting expense submission tests at {datetime.now()}")
    print("=" * 50)
    
    for test_case in TEST_CASES:
        submit_expense(test_case)
        print("=" * 50)

def create_receipt_directories():
    """Create necessary directories for receipts if they don't exist"""
    directories = ["receipt_path"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

if __name__ == "__main__":
    # Create necessary directories
    create_receipt_directories()
    
    # Run the tests
    run_all_tests()