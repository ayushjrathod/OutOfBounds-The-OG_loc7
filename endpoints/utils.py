import base64
from datetime import datetime
import uuid
import google.generativeai as genai
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import tempfile
import json
import PyPDF2
from groq import Groq
import re
import mimetypes

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
    bill_number: Optional[str] = None
    categories: List[str]  # Add categories field
    content_type: str  # Add content_type to the ExpenseCreate model

def encode_image(image_bytes: bytes) -> str:
    """Encode image bytes to base64 string with proper padding"""
    try:
        # Remove any whitespace and newlines from the base64 string
        base64_data = base64.b64encode(image_bytes).decode('utf-8').strip()
        
        # Add padding if needed
        missing_padding = len(base64_data) % 4
        if missing_padding:
            base64_data += '=' * (4 - missing_padding)
            
        return base64_data
    except Exception as e:
        print(f"Error in encode_image: {str(e)}")
        raise ValueError("Failed to encode image")

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

def analyze_receipt(base64_data: str, content_type: str = "image/jpeg") -> dict:
    try:
        # For PDF files - use Groq
        if content_type == "application/pdf":
            pdf_bytes = base64.b64decode(base64_data)
            text_content = extract_text_from_pdf(pdf_bytes)
            return analyze_receipt_text(text_content)  # This uses Groq
            
        # For images - use Gemini Vision
        elif content_type in ["image/jpeg", "image/jpg", "image/png"]:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(base64.b64decode(base64_data))
                temp_path = temp_file.name

            try:
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

                # Upload image to Gemini
                image = genai.upload_file(temp_path, mime_type=content_type)

                # Start chat session with Gemini
                chat = model.start_chat()
                response = chat.send_message([
                    image,
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

                # Parse Gemini response
                parsed_data = json.loads(re.search(r'({[\s\S]*})', response.text).group(1))
                
                # Clean up prices
                for item in parsed_data.get('items', []):
                    item['price'] = float(str(item['price']).replace('$', '').replace(',', ''))
                parsed_data['total_amount'] = float(str(parsed_data.get('total_amount', 0)).replace('$', '').replace(',', ''))

                return parsed_data

            finally:
                # Clean up temp file
                os.unlink(temp_path)
        
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

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

def process_expense(expense: ExpenseCreate, db) -> dict:
    try:
        content_type = expense.content_type
        
        # Skip file saving for Cloudinary URLs
        if content_type == "image/url":
            # For URLs, we'll analyze the receipt differently or skip analysis
            receipt_data = {
                "items": [],
                "total_amount": 0.0,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "vendor": expense.vendor or "Unknown",
                "bill_number": None
            }
        else:
            # Original file processing logic for non-URL uploads
            try:
                # Create the server_files directory if it doesn't exist
                server_files_dir = "server_files"
                if not os.path.exists(server_files_dir):
                    os.makedirs(server_files_dir)

                # Generate a unique filename
                file_extension = mimetypes.guess_extension(content_type)
                filename = f"{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(server_files_dir, filename)

                # Decode base64 and save the file
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(expense.receipt_image))
            except Exception as e:
                raise ValueError(f"Failed to save receipt file: {str(e)}")

            # Process receipt based on content type
            if content_type == "application/pdf":
                pdf_bytes = base64.b64decode(expense.receipt_image)
                text_content = extract_text_from_pdf(pdf_bytes)
                receipt_data = analyze_receipt_text(text_content)
            else:
                # For images (jpeg, jpg, png)
                receipt_data = analyze_receipt(expense.receipt_image, content_type)

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
        
        expense_doc = {
            "employeeId": expense.employeeId,
            "departmentId": expense.departmentId,
            "expenses": [{
                "expenseId": str(uuid.uuid4()),
                "expenseType": expense.expenseType,
                "amount": float(receipt_data.get("total_amount", 0.0)),
                "date": receipt_data.get("date", current_date),
                "vendor": receipt_data.get("vendor", expense.vendor or "Unknown"),
                "description": expense.description,
                "categories": expense.categories,
                "receiptImage": expense.receipt_image,  # Store Cloudinary URL directly
                "bill_number": receipt_data.get("bill_number"),
                "item_details": receipt_data.get("items", []),
                "aiSummary": json.dumps(receipt_data),
                "status": "Pending",  # Default status
                "submittedDate": current_date,
                "approvedBy": "",  # Changed to empty string
                "approvalDate": "",  # Changed to empty string
                "rejectionReason": "",  # Changed to empty string
                "fraudScore": 0.0,  # Changed to 0.0
                "isAnomaly": False,  # Changed to False
                "createdAt": current_time,
                "updatedAt": current_time
            }]
        }
        print(expense_doc)
        
        return db.EmployeeExpenses.insert_one(expense_doc)
    except Exception as e:
        raise ValueError(f"Failed to process receipt: {str(e)}")
