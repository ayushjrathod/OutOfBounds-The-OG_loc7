from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
from dotenv import load_dotenv
from view_expense import view_expense_details

load_dotenv()

def delete_all_expenses():
    try:
        # Connect to MongoDB
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB
        
        # Get count of documents
        count = db.EmployeeExpenses.count_documents({})
        
        if count == 0:
            print("\nNo expenses found in the database.")
            return
            
        print(f"\nWARNING: This will delete all {count} expense documents!")
        confirm = input("Are you sure you want to delete ALL expenses? Type 'DELETE ALL' to confirm: ")
        
        if confirm != "DELETE ALL":
            print("Deletion cancelled.")
            return
            
        # Delete all documents
        result = db.EmployeeExpenses.delete_many({})
        print(f"\nSuccess: Deleted {result.deleted_count} expense documents.")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

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
    print("\nExpense Deletion Tool")
    print("1. Delete single expense")
    print("2. Delete ALL expenses")
    choice = input("\nEnter your choice (1/2): ")
    
    if choice == "1":
        expense_id = input("Enter expense ID to delete: ")
        delete_expense(expense_id)
    elif choice == "2":
        delete_all_expenses()
    else:
        print("Invalid choice. Please select 1 or 2.")
