from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils import ExpenseCreate, process_expense, encode_image
import mimetypes
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB Atlas connection with error handling
try:
    uri = os.getenv('MONGO_URL_prathamesh')
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Test the connection
    client.admin.command('ping')
    db = client.expensesDB
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/api/expenses/")
async def create_expense(
    employeeId: str = Form(...),
    departmentId: str = Form(...),
    expenseType: str = Form(...),
    description: str = Form(...),
    vendor: str = Form(None),
    receipt: UploadFile = File(...)
):
    # Validate file type
    content_type = receipt.content_type
    if not content_type:
        content_type, _ = mimetypes.guess_type(receipt.filename)
    
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
    if not content_type or not any(content_type.startswith(t) for t in allowed_types):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Supported types: {', '.join(allowed_types)}"
        )
        
    try:
        # Limit file size (e.g., 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_bytes = await receipt.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size too large. Maximum size: {MAX_FILE_SIZE/1024/1024:.1f}MB"
            )
            
        base64_file = encode_image(file_bytes)
        
        # Create expense object with content type
        expense = ExpenseCreate(
            employeeId=employeeId,
            departmentId=departmentId,
            expenseType=expenseType,
            description=description,
            vendor=vendor,
            receipt_image=base64_file,
            content_type=content_type  # Add content type
        )
        
        # Process and store the expense
        result = process_expense(expense, db)
        return {
            "status": "success", 
            "expense_id": str(result.inserted_id),
            "message": "Expense processed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing expense: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing the expense"
        )
