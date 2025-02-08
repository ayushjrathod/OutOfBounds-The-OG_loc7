from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from dotenv import load_dotenv
from view_expense import view_expense_details

load_dotenv()

def delete_expense(expense_id: str):
    try:
        # Connect to MongoDB
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        # Convert string ID to ObjectId
        expense_obj_id = ObjectId(expense_id)
        
        # First, show the expense details
        print("\nExpense to be deleted:")
        view_expense_details(expense_id)
        
        # Confirm deletion
        confirm = input("\nAre you sure you want to delete this expense? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            return
        
        # Delete the expense
        result = db.EmployeeExpenses.delete_one({"_id": expense_obj_id})
        
        if result.deleted_count == 1:
            print(f"\nSuccess: Expense with ID {expense_id} has been deleted.")
        else:
            print(f"\nError: No expense found with ID {expense_id}")

        client.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Get expense ID from command line or use default
    import sys
    expense_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter expense ID to delete: ")
    delete_expense(expense_id)
