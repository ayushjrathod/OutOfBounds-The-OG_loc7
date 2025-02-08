import base64
from datetime import datetime
import uuid
from groq import Groq
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ItemDetail(BaseModel):
    item: str
    amount: float

class ExpenseCreate(BaseModel):
    employeeId: str
    departmentId: str
    expenseType: str
    description: str
    receipt_image: str
    vendor: Optional[str] = None

def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_receipt(base64_image: str) -> dict:
    # Initialize Groq client with API key
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY')
    )
    
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the following information from this receipt: total amount, date, vendor name, and itemized list with prices. Format as JSON."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }],
        model="llama-3.2-11b-vision-preview",
    )
    
    return chat_completion.choices[0].message.content

def analyze_receipt(base64_image: str) -> dict:
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY')
    )
    
    chat_completion = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """Please analyze this receipt and extract:
                1. Item names and their individual prices
                2. Total amount
                3. Date of purchase
                4. Vendor/store name
                
                Format the response as JSON with this structure:
                {
                    "items": [
                        {"name": "item name", "price": 0.00},
                        ...
                    ],
                    "total_amount": 0.00,
                    "date": "YYYY-MM-DD",
                    "vendor": "store name"
                }"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }],
        model="llama-3.2-11b-vision-preview",
    )
    
    return chat_completion.choices[0].message.content

def process_expense(expense: ExpenseCreate, db) -> dict:
    receipt_analysis = analyze_receipt(expense.receipt_image)
    
    # Parse the JSON response from Groq
    try:
        import json
        receipt_data = json.loads(receipt_analysis)
        
        # Create expense document with itemized details
        expense_doc = {
            "employeeId": expense.employeeId,
            "departmentId": expense.departmentId,
            "expenses": [{
                "expenseId": str(uuid.uuid4()),
                "expenseType": expense.expenseType,
                "amount": receipt_data.get("total_amount", 0.0),
                "date": receipt_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "vendor": receipt_data.get("vendor", expense.vendor),
                "description": expense.description,
                "receiptImage": expense.receipt_image,
                "item_details": receipt_data.get("items", []),
                "aiSummary": receipt_analysis,
                # ...rest of the fields...
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }]
        }
        
        return db.EmployeeExpenses.insert_one(expense_doc)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse receipt analysis")