from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils import ExpenseCreate, process_expense, encode_image
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
    uri = os.getenv('MONGO_URL_samyak')
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
    if not receipt.content_type.startswith(('image/', 'application/pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image or PDF.")
        
    try:
        # Limit file size (e.g., 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        image_bytes = await receipt.read()
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size too large")
            
        base64_image = encode_image(image_bytes)
        
        # Create expense object
        expense = ExpenseCreate(
            employeeId=employeeId,
            departmentId=departmentId,
            expenseType=expenseType,
            description=description,
            vendor=vendor,
            receipt_image=base64_image
        )
        
        # Process and store the expense
        result = process_expense(expense, db)
        print(f"Expense created with ID: {result.inserted_id}")
        return {"status": "success", "expense_id": str(result.inserted_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
