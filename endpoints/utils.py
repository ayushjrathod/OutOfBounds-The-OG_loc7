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
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY')
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": """Please analyze this receipt and provide the output in valid JSON format:
                    {
                        "items": [
                            {"name": "item name", "price": 0.00}
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
        
        response_content = chat_completion.choices[0].message.content
        
        # Try to extract JSON from the response if it's wrapped in other text
        import re
        json_match = re.search(r'({[\s\S]*})', response_content)
        if json_match:
            response_content = json_match.group(1)
            
        # Validate JSON structure
        import json
        parsed_data = json.loads(response_content)
        
        # Ensure required fields exist
        required_fields = ["items", "total_amount", "date", "vendor"]
        if not all(field in parsed_data for field in required_fields):
            return {
                "items": [],
                "total_amount": 0.0,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "vendor": "Unknown"
            }
            
        return parsed_data
        
    except Exception as e:
        print(f"Error analyzing receipt: {str(e)}")
        # Return a default structure if analysis fails
        return {
            "items": [],
            "total_amount": 0.0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "vendor": "Unknown"
        }

def process_expense(expense: ExpenseCreate, db) -> dict:
    try:
        receipt_data = analyze_receipt(expense.receipt_image)
        
        expense_doc = {
            "employeeId": expense.employeeId,
            "departmentId": expense.departmentId,
            "expenses": [{
                "expenseId": str(uuid.uuid4()),
                "expenseType": expense.expenseType,
                "amount": float(receipt_data.get("total_amount", 0.0)),
                "date": receipt_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                "vendor": receipt_data.get("vendor", expense.vendor or "Unknown"),
                "description": expense.description,
                "receiptImage": expense.receipt_image,
                "item_details": receipt_data.get("items", []),
                "aiSummary": receipt_data,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }]
        }
        
        return db.EmployeeExpenses.insert_one(expense_doc)
    except Exception as e:
        raise ValueError(f"Failed to process receipt: {str(e)}")
