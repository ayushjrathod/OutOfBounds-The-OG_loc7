from datetime import datetime
import uuid
import google.generativeai as genai
import os
from dotenv import load_dotenv
import tempfile
import json
import PyPDF2
from groq import Groq
import re
import requests
from models import ExpenseCreate, ItemDetail  # Import ItemDetail from models.py
from db import db
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name
            
        text = ""
        with open(temp_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
                
        os.unlink(temp_path)
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return ""

def analyze_receipt_text(text: str) -> dict:
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a receipt analysis expert. Your task is to extract detailed information from receipts and format it as JSON. Currency in INR."
                },
                {
                    "role": "user",
                    "content": f"""Analyze this receipt text and extract key information.
                    Text content: {text}
                    
                    Provide the output in this exact JSON format:
                    {{
                        "items": [
                            {{"name": "item name", "price": 0.00}}
                        ],
                        "total_amount": 0.00,
                        "date": "YYYY-MM-DD",
                        "vendor": "store name",
                        "bill_number": "receipt number/bill number"
                    }}
                    
                    Rules:
                    - Extract all items and their exact prices
                    - Format total amount as number
                    - Format date as YYYY-MM-DD
                    - Include store/vendor name
                    - Include bill/receipt number if present"""
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stream=False
        )
        
        response_content = chat_completion.choices[0].message.content
        
        # Extract and parse JSON
        json_match = re.search(r'({[\s\S]*})', response_content)
        if not json_match:
            raise ValueError("No valid JSON found in response")
            
        parsed_data = json.loads(json_match.group(1))
        
        # Clean up prices
        for item in parsed_data.get('items', []):
            item['price'] = float(str(item['price']).replace('$', '').replace(',', ''))
        parsed_data['total_amount'] = float(str(parsed_data.get('total_amount', 0)).replace('$', '').replace(',', ''))
        
        return parsed_data
        
    except Exception as e:
        print(f"Error analyzing receipt text: {str(e)}")
        return {
            "items": [],
            "total_amount": 0.0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "vendor": "Unknown",
            "bill_number": None,
            "error": str(e)
        }

def analyze_receipt(receipt_url: str, content_type: str = "image/url") -> dict:
    try:
        if (content_type == "image/url"):
            # Configure Gemini
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=generation_config,
            )

            # Send URL directly to Gemini
            chat = model.start_chat()
            response = chat.send_message([
                receipt_url,
                """Analyze this receipt and provide output in this exact JSON format:
                {
                    "items": [{"name": "item name", "price": 0.00}],
                    "total_amount": 0.00,
                    "date": "YYYY-MM-DD",
                    "vendor": "store name",
                    "bill_number": "receipt number/bill number"
                }
                Extract every item, exact prices, and bill/receipt number if visible."""
            ])

            # Parse response
            parsed_data = json.loads(re.search(r'({[\s\S]*})', response.text).group(1))
            
            # Clean up prices
            for item in parsed_data.get('items', []):
                item['price'] = float(str(item['price']).replace('$', '').replace(',', ''))
            parsed_data['total_amount'] = float(str(parsed_data.get('total_amount', 0)).replace('$', '').replace(',', ''))

            return parsed_data

    except Exception as e:
        print(f"Error in receipt analysis: {str(e)}")
        return {
            "items": [],
            "total_amount": 0.0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "vendor": "Unknown",
            "bill_number": None,
            "error": str(e)
        }

def evaluate_appeal(appeal: str) -> dict:
    """Evaluate expense appeal using Groq LLM"""
    prompt_text = f'''
    This following is a reciept reimbursement appeal. You have to rate it from 0 to 1 on a suspicious score. With factors like:

    1.Exceeding limits, you can refer to this for a typical employee:
    {{
        "expensePolicies": [
            {{
                "department": "HR",
                "maxAnnualSpend": 30000.0,
                "maxMonthlySpend": 2500.0,
                "maxPerExpenseSpend": 600.0,
                "allowedExpensecategories": [
                    {{"category": "Travel Expenses", "maxSpend": 300.0}},
                    {{"category": "Work Equipment & Supplies", "maxSpend": 250.0}},
                    {{"category": "Meals & Entertainment", "maxSpend": 350.0}},
                    {{"category": "Internet & Phone Bills", "maxSpend": 100.0}},
                    {{"category": "Professional Development", "maxSpend": 700.0}},
                    {{"category": "Health & Wellness", "maxSpend": 500.0}},
                    {{"category": "Commuting Expenses", "maxSpend": 200.0}},
                    {{"category": "Software & Subscriptions", "maxSpend": 150.0}},
                    {{"category": "Relocation Assistance", "maxSpend": 0.0}},
                    {{"category": "Client & Marketing Expenses", "maxSpend": 300.0}}
                ]
            }}
        ]
    }}
    2. Category Not matching the descrpition or the contents
    3. Billed outside business hours
    4. Unusually high rates for common expenses (example: luxury dining listed as meal)

    this is the appeal you have to evaluate:
    {appeal}

    give a score in this format: sus_score = <score>
    also give a very conscise reason for the score and your conclusion in this format: reason = <reason>
    '''

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": prompt_text
        }]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        response.raise_for_status()
        result = response.json()
        model_response = result.get("choices", [{}])[0].get("message", {}).get("content", "No response found")
        
        # Extract score and reason
        score_match = re.search(r"sus_score = ([\d.]+)", model_response)
        reason_match = re.search(r"reason = (.+)$", model_response, re.MULTILINE)
        
        return {
            "score": float(score_match.group(1)) if score_match else 0.0,
            "reason": reason_match.group(1).strip() if reason_match else "No reason provided"
        }
    except Exception as e:
        print(f"Error in evaluate_appeal: {str(e)}")
        return {"score": 0.0, "reason": str(e)}

def process_expense(expense: ExpenseCreate, db) -> dict:
    try:
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Test the connection
        client.admin.command('ping')
        db = client.expensesDB
        # Use the Cloudinary URL directly for analysis
        receipt_data = analyze_receipt(expense.receipt_image)

        # Check if bill number already exists
        bill_number = receipt_data.get('bill_number')
        if bill_number:
            existing_expense = db.EmployeeExpenses.find_one({
                "expenses.bill_number": bill_number
            })
            if existing_expense:
                raise ValueError(f"Receipt with bill number {bill_number} already exists")

        # Convert timestamps to string format
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Prepare appeal data for evaluation
        appeal_data = {
            "expenseType": expense.expenseType,
            "amount": float(receipt_data.get("total_amount", 0.0)),
            "date": receipt_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "vendor": receipt_data.get("vendor", expense.vendor or "Unknown"),
            "description": expense.description,
            "categories": expense.categories,
            "items": receipt_data.get("items", []),
            "receipt_url": expense.receipt_image  # Include Cloudinary URL in appeal data
        }

        # Get fraud evaluation
        evaluation = evaluate_appeal(json.dumps(appeal_data))
        
        # Create expense document with only necessary fields
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
                "categories": expense.categories,
                "receiptImage": expense.receipt_image,  # Store Cloudinary URL
                "bill_number": receipt_data.get("bill_number"),
                "item_details": receipt_data.get("items", []),
                "aiSummary": evaluation["reason"],
                "status": "Pending",
                "submittedDate": datetime.now().strftime("%Y-%m-%d"),
                "fraudScore": evaluation["score"],
                "isAnomaly": evaluation["score"] > 0.7,
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        print("Storing expense with receipt URL:", expense.receipt_image)
        
        result = db.EmployeeExpenses.insert_one(expense_doc)
        return result
    except Exception as e:
        raise ValueError(f"Failed to process receipt: {str(e)}")