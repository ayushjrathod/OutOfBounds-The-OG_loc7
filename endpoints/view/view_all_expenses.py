from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

def format_datetime(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return obj

def view_all_expenses():
    try:
        # Connect to MongoDB
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        # Query all expenses
        expenses = list(db.EmployeeExpenses.find())
        
        if not expenses:
            print("No expenses found in the database.")
            return

        # Print summary of all expenses
        print("\n=== All Expenses Summary ===")
        
        summary_data = []
        total_amount = 0

        for expense in expenses:
            for exp in expense['expenses']:
                summary_data.append([
                    str(expense['_id']),
                    expense['employeeId'],
                    expense['departmentId'],
                    exp['expenseType'],
                    f"₹{exp['amount']:.2f}",
                    exp['date'],
                    exp['vendor'],
                    exp.get('bill_number', 'N/A'),
                    format_datetime(exp['createdAt'])
                ])
                total_amount += exp['amount']

        # Print table using tabulate
        headers = ['ID', 'Employee', 'Department', 'Type', 'Amount', 'Date', 'Vendor', 'Bill No.', 'Created']
        print(tabulate(summary_data, headers=headers, tablefmt='grid'))
        
        # Print summary statistics
        print(f"\nTotal Expenses: {len(summary_data)}")
        print(f"Total Amount: ₹{total_amount:.2f}")

        # Option to view detailed information
        while True:
            choice = input("\nEnter expense ID to view details (or 'q' to quit): ")
            if choice.lower() == 'q':
                break
                
            # Import and use the existing view_expense_details function
            from view_expense import view_expense_details
            view_expense_details(choice)

        client.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    view_all_expenses()
