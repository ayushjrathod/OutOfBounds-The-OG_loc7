import requests
import os
import mimetypes

VALID_EMPLOYEE_IDS = [f"EMP00{i}" for i in range(1, 6)]
VALID_DEPARTMENT_IDS = [f"DEP00{i}" for i in range(1, 6)]
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

def test_expense_submissions():
    # API endpoint
    url = "http://localhost:8000/api/expenses/"
    
    # Test directory with receipt files
    receipt_dir = "receipt images"
    if not os.path.exists(receipt_dir):
        print(f"Error: Receipt directory not found: {receipt_dir}")
        return

    # Test each valid employee with different categories and receipts
    for emp_id in VALID_EMPLOYEE_IDS:
        dept_id = f"DEP00{emp_id[-1]}"  # Match department with employee
        
        # Get list of receipt files
        receipt_files = [f for f in os.listdir(receipt_dir) if os.path.isfile(os.path.join(receipt_dir, f))]
        
        if not receipt_files:
            print(f"No receipt files found in {receipt_dir}")
            return

        # Test each receipt with a different category
        for receipt_file, category in zip(receipt_files, VALID_EXPENSE_CATEGORIES):
            file_path = os.path.join(receipt_dir, receipt_file)
            
            # Form data
            data = {
                "employeeId": emp_id,
                "departmentId": dept_id,
                "expenseType": category,
                "description": f"Test expense for {category}",
                "vendor": "Test Vendor",
                "categories": category
            }
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'image/jpeg'
            
            print(f"\nTesting expense submission:")
            print(f"Employee: {emp_id}")
            print(f"Department: {dept_id}")
            print(f"Category: {category}")
            print(f"File: {receipt_file}")
            
            try:
                with open(file_path, 'rb') as f:
                    files = {
                        'receipt': (receipt_file, f, content_type)
                    }
                    response = requests.post(url, data=data, files=files)
                    
                print(f"Status Code: {response.status_code}")
                print("Response:", response.json())
                
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_expense_submissions()
