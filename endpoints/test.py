import requests
import os

def test_expense_submission():
    # API endpoint
    url = "http://localhost:8000/api/expenses/"
    
    # Form data
    data = {
        "employeeId": "EMP123",
        "departmentId": "DEP456",
        "expenseType": "client_meeting",
        "description": "client Dolph AI request",
        "vendor": "Restaurant ABC"
    }
    
    # Receipt file path
    receipt_path = "receipt images/dmart.jpg"
    
    # Verify file exists
    if not os.path.exists(receipt_path):
        print(f"Error: Receipt file not found at {receipt_path}")
        return
    
    # Create files dict with receipt
    files = {
        'receipt': ('dmart.jpg', open(receipt_path, 'rb'), 'image/jpeg')
    }
    
    try:
        # Send POST request
        response = requests.post(url, data=data, files=files)
        
        # Print response
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(response.json())
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Close the file
        files['receipt'][1].close()

if __name__ == "__main__":
    test_expense_submission()
