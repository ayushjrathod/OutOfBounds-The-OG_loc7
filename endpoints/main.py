from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils import ExpenseCreate, process_expense, encode_image
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MongoDB Atlas connection with error handling
try:
    uri = os.getenv('MONGO_URL')
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
    try:
        # Read and encode the receipt image
        image_bytes = await receipt.read()
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
        return {"status": "success", "expense_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
