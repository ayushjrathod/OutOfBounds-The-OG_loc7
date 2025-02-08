from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

def format_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return obj

def view_expense_details(expense_id: str):
    try:
        # Connect to MongoDB
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        # Convert string ID to ObjectId
        expense_obj_id = ObjectId(expense_id)
        
        # Query the database
        expense = db.EmployeeExpenses.find_one({"_id": expense_obj_id})
        
        if not expense:
            print(f"No expense found with ID: {expense_id}")
            return

        # Format and display the expense details
        print("\n=== Expense Details ===")
        print(f"ID: {expense_id}")
        print(f"Employee ID: {expense['employeeId']}")
        print(f"Department ID: {expense['departmentId']}")
        
        for exp in expense['expenses']:
            print("\n--- Expense Entry ---")
            print(f"Expense ID: {exp['expenseId']}")
            print(f"Type: {exp['expenseType']}")
            print(f"Amount: ${exp['amount']:.2f}")
            print(f"Date: {exp['date']}")
            print(f"Vendor: {exp['vendor']}")
            print(f"Description: {exp['description']}")
            print(f"Bill Number: {exp.get('bill_number', 'Not provided')}")
            
            print("\nItems:")
            for item in exp['item_details']:
                print(f"- {item['name']}: ${item['price']:.2f}")
            
            print(f"\nCreated: {format_datetime(exp['createdAt'])}")
            print(f"Updated: {format_datetime(exp['updatedAt'])}")

        client.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Get expense ID from command line or use default
    import sys
    expense_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter expense ID: ")
    view_expense_details(expense_id)
