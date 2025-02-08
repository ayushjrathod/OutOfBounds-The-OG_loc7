from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os
import base64
from dotenv import load_dotenv
import mimetypes

load_dotenv()

def save_receipt(expense_id: str, output_dir: str = "downloaded_receipts"):
    try:
        # Connect to MongoDB
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Find expense by expenseId instead of _id
        expense = db.EmployeeExpenses.find_one({
            "expenses.expenseId": expense_id
        })
        
        if not expense:
            print(f"No expense found with ID: {expense_id}")
            return

        # Get the specific expense entry
        target_expense = None
        for exp in expense['expenses']:
            if exp['expenseId'] == expense_id:
                target_expense = exp
                break

        if target_expense and 'receiptImage' in target_expense:
            # Get file type
            file_type = target_expense.get('file_type', 'image/jpeg')
            extension = mimetypes.guess_extension(file_type) or '.jpg'
            
            # Clean and validate base64 data
            try:
                base64_data = target_expense['receiptImage'].strip()
                # Add padding if needed
                missing_padding = len(base64_data) % 4
                if missing_padding:
                    base64_data += '=' * (4 - missing_padding)
                
                # Attempt to decode
                image_data = base64.b64decode(base64_data)
            except Exception as e:
                print(f"Error decoding base64: {str(e)}")
                return
            
            # Generate filename
            filename = f"receipt_{expense_id}{extension}"
            filepath = os.path.join(output_dir, filename)
            
            # Save the file
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            print(f"\nReceipt saved as: {filepath}")
            print(f"File type: {file_type}")
            print(f"Original vendor: {target_expense.get('vendor', 'Unknown')}")
            print(f"Date: {target_expense.get('date', 'Unknown')}")
            
            # If it's a PDF, show text content
            if file_type == 'application/pdf':
                print("\nPDF Content:")
                try:
                    import PyPDF2
                    with open(filepath, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            print(page.extract_text())
                except Exception as e:
                    print(f"Could not extract PDF text: {str(e)}")
        else:
            print("No receipt image found in the expense record")

        client.close()

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Get expense ID from command line or use default
    import sys
    expense_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter expense ID: ")
    save_receipt(expense_id)
