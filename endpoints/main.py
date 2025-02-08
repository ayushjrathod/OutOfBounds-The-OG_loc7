from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
    uri = os.getenv('MONGODB_URL_neha')
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Test the connection
    client.admin.command('ping')
    db = client.expensesDB
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Database connection failed")

VALID_EXPENSE_CATEGORIES = [
    "Travel Expenses",
    "Work Equipment & Supplies",
    "Meals & Entertainment",
    "Internet & Phone Bills",
    "Professional Development",
    "Health & Wellness",
    "Commuting Expenses",
    "Software & Subscriptions",
    "Relocation Assistance",
    "Client & Marketing Expenses"
]

# Remove constants for valid IDs
# VALID_EMPLOYEE_IDS = [f"EMP{i}" for i in range(1, 6)]
# VALID_DEPARTMENT_IDS = [f"DEP00{i}" for i in range(1, 6)]

@app.post("/api/expenses/")
async def create_expense(
    employeeId: str = Form(...),
    departmentId: str = Form(...),
    expenseType: str = Form(...),
    description: str = Form(...),
    vendor: str = Form(None),
    categories: str = Form(...),
    receiptImage: str = Form(...)  # Changed from receipt: UploadFile
):
    # First validate employee and department existence
    try:
        # Check if employee exists in the correct department
        query = {
            "departmentId": departmentId,
            "employees": {
                "$elemMatch": {
                    "id": employeeId
                }
            }
        }
        print("Executing query:", query)  # Log the query
        department_employee = db.DepartmentsEmployees.find_one(query)
        print("Query result:", department_employee)  # Log the result
        
        if not department_employee:
            # If not found, check if it's because of invalid IDs
            # Remove hardcoded validation
            # if employeeId not in VALID_EMPLOYEE_IDS:
            #     raise HTTPException(
            #         status_code=400,
            #         detail=f"Invalid employee ID. Must be one of: {', '.join(VALID_EMPLOYEE_IDS)}"
            #     )
            
            # If IDs are valid but relationship not found
            raise HTTPException(
                status_code=400,
                detail=f"Employee {employeeId} is not associated with department {departmentId}"
            )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail="Error validating employee and department relationship"
        )

    # Validate expense type
    if categories not in VALID_EXPENSE_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid expense type. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
        )
    
    # Validate and parse categories
    try:
        categories_list = [cat.strip() for cat in categories.split(',')]
        for cat in categories_list:
            if cat not in VALID_EXPENSE_CATEGORIES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category: {cat}. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
                )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Categories must be comma-separated values"
        )

    try:
        # Create expense object with Cloudinary URL
        expense = ExpenseCreate(
            employeeId=employeeId,
            departmentId=departmentId,
            expenseType=expenseType,
            description=description,
            vendor=vendor,
            categories=categories_list,
            receipt_image=receiptImage,  # Use Cloudinary URL
            content_type="image/url"  # New content type for URLs
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

@app.get("/api/files/{file_path:path}")
async def get_file(file_path: str):
    """
    Retrieve a file from the server_files directory.
    """
    full_path = os.path.join("server_files", file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)
