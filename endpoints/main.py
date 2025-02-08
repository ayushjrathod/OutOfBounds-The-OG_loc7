from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils import ExpenseCreate, process_expense
import mimetypes
import os
from dotenv import load_dotenv
from google import genai
from datetime import datetime
from typing import List, Dict, Any
from notification_utils import send_email, create_expense_email, create_admin_approval_email
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

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
    receiptImage: str = Form(...),  # Changed to accept Cloudinary URL
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
            receipt_image=receiptImage,  # Use Cloudinary URL directly
            content_type="image/url"
        )
        
        # Process and store the expense
        result = process_expense(expense, db)
        expense_id = str(result.inserted_id)

        # Get the stored expense document
        stored_expense = db.EmployeeExpenses.find_one({"_id": result.inserted_id})
        expense_details = stored_expense["expenses"][0]

        # Send confirmation email to employee
        employee_email = "samyaknahar81@gmail.com"  # Replace with actual employee email
        html_content = create_expense_email("pending", expense_id)
        send_email(
            employee_email,
            "Expense Request Received",
            html_content
        )

        # Send approval request to admin
        admin_email = "samyaknahar004@gmail.com"
        admin_html_content = create_admin_approval_email(
            expense_id=expense_id,
            employee_id=expense.employeeId,
            amount=expense_details["amount"],
            ai_summary=expense_details["aiSummary"],
            fraud_score=expense_details["fraudScore"]
        )
        
        admin_email_success, admin_email_message = send_email(
            admin_email,
            f"Expense Approval Required - {expense.employeeId}",
            admin_html_content
        )

        return {
            "status": "success", 
            "expense_id": expense_id,
            "message": "Expense processed successfully",
            "admin_notification_sent": admin_email_success
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing expense: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing the expense"
        )

# Add new endpoint for updating expense status with email notification
@app.post("/api/expenses/{expense_id}/status")
async def update_expense_status(
    expense_id: str,
    status: str = Form(...),
    reason: str = Form(None)
):
    try:
        # Find the expense
        expense = db.EmployeeExpenses.find_one({"_id": expense_id})
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        # Get employee email from your employee collection
        employee = db.Employees.find_one({"employeeId": expense["employeeId"]})
        if not employee or "email" not in employee:
            raise HTTPException(status_code=400, detail="Employee email not found")

        # Update status
        db.EmployeeExpenses.update_one(
            {"_id": expense_id},
            {"$set": {"status": status, "statusReason": reason}}
        )

        # Send status update email
        html_content = create_expense_email(status, expense_id, reason)
        email_success, email_message = send_email(
            employee["email"],
            f"Expense Request {status.capitalize()}",
            html_content
        )

        return {
            "status": "success",
            "message": f"Expense status updated to {status}",
            "email_sent": email_success,
            "email_status": email_message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Remove the /api/files endpoint since we're using Cloudinary

# MongoDB connection setup
emp_bot_mongo_uri = "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
emp_bot_client = MongoClient(emp_bot_mongo_uri)
emp_bot_db = emp_bot_client.expensesDB

# GenAI API setup
emp_bot_genai_client = genai.Client(api_key="AIzaSyCTrlYfp3NRqIhcxenlPBIB8Kr5iIDBWgc")

def emp_bot_get_employee_expenses(emp_bot_employee_id):
    # Fetch the employee expenses by employee ID
    emp_bot_employee_expenses = emp_bot_db.EmployeeExpenses.find_one({"employeeId": emp_bot_employee_id})

    if not emp_bot_employee_expenses:
        return None

    # Remove MongoDB-specific fields like "_id"
    if "_id" in emp_bot_employee_expenses:
        del emp_bot_employee_expenses["_id"]

    return emp_bot_employee_expenses

def emp_bot_query_genai(emp_bot_employee_expenses, emp_bot_question):
    # Define the prompt
    emp_bot_text = f'''
    You are a helpful data-driven assistant. You are given the information of an employee's spending habits. Ignore the IDs and do not tell the user about the IDs.

    {emp_bot_employee_expenses}

    See this data and answer the user's question below:
    {emp_bot_question}

    Keep this in mind as a general knowledge in case the user asks. This is a general policy of the spending allowances of the company. Use this info if the question requires it:

    (Expense Policies go here...)
    '''

    # Generate the response from GenAI
    emp_bot_response = emp_bot_genai_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=emp_bot_text,
    )

    return emp_bot_response.text

@app.post("/emp_bot/query")
async def emp_bot_handle_query(request: Request):
    # Parse the request body as JSON
    query_data = await request.json()

    # Extract employee_id and question from the request body
    employee_id = query_data.get("employee_id")
    question = query_data.get("question")

    if not employee_id or not question:
        raise HTTPException(status_code=400, detail="Missing employee_id or question in the request body.")

    # Get employee expenses
    emp_bot_expenses = emp_bot_get_employee_expenses(employee_id)

    if not emp_bot_expenses:
        raise HTTPException(status_code=404, detail="No expenses found for the given employee ID.")

    # Query GenAI
    emp_bot_response_text = emp_bot_query_genai(emp_bot_expenses, question)

    return {"response": emp_bot_response_text}

# Add analytics endpoints
@app.get("/api/analytics/department-expenses")
async def get_department_expenses():
    """Get total expenses by department"""
    pipeline = [
        {"$unwind": "$expenses"},
        {
            "$group": {
                "_id": "$departmentId",
                "total_amount": {"$sum": "$expenses.amount"}
            }
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/monthly-trends")
async def get_monthly_trends():
    """Get expense trends by month"""
    pipeline = [
        {"$unwind": "$expenses"},
        {
            "$project": {
                "month": {
                    "$dateFromString": {
                        "dateString": "$expenses.date",
                        "format": "%Y-%m-%d"
                    }
                },
                "amount": "$expenses.amount"
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$month"},
                    "month": {"$month": "$month"}
                },
                "total_amount": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/category-distribution")
async def get_category_distribution():
    """Get expense distribution by category"""
    pipeline = [
        {"$unwind": "$expenses"},
        {"$unwind": "$expenses.categories"},
        {
            "$group": {
                "_id": "$expenses.categories",
                "total_amount": {"$sum": "$expenses.amount"},
                "count": {"$sum": 1}
            }
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/fraud-analysis")
async def get_fraud_analysis():
    """Get fraud score analysis"""
    pipeline = [
        {"$unwind": "$expenses"},
        {
            "$group": {
                "_id": {
                    "departmentId": "$departmentId",
                    "isAnomaly": "$expenses.isAnomaly"
                },
                "count": {"$sum": 1},
                "avg_fraud_score": {"$avg": "$expenses.fraudScore"}
            }
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/vendor-spending")
async def get_vendor_spending():
    """Get spending by vendor"""
    pipeline = [
        {"$unwind": "$expenses"},
        {
            "$group": {
                "_id": "$expenses.vendor",
                "total_amount": {"$sum": "$expenses.amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_amount": -1}},
        {"$limit": 10}
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/employee-expenses")
async def get_employee_expenses():
    """Get total expenses by employee"""
    pipeline = [
        {"$unwind": "$expenses"},
        {
            "$group": {
                "_id": "$employeeId",
                "total_amount": {"$sum": "$expenses.amount"},
                "transaction_count": {"$sum": 1},
                "avg_amount": {"$avg": "$expenses.amount"},
                "departments": {"$addToSet": "$departmentId"}
            }
        },
        {"$sort": {"total_amount": -1}}
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/employee-categories")
async def get_employee_categories():
    """Get category-wise spending for each employee"""
    pipeline = [
        {"$unwind": "$expenses"},
        {"$unwind": "$expenses.categories"},
        {
            "$group": {
                "_id": {
                    "employeeId": "$employeeId",
                    "category": "$expenses.categories"
                },
                "total_amount": {"$sum": "$expenses.amount"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"total_amount": -1}}
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

# Update the MongoDB connection to use environment variables
try:
    uri = os.getenv('MONGO_URL')
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    db = client.expensesDB
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Database connection failed")

# Add new models
class ExpenseStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None

# Add new endpoints
@app.post("/api/expenses/{expense_id}/accept")
async def accept_expense(expense_id: str, reason: str = None):
    try:
        # Convert string ID to ObjectId
        expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        # Update expense status
        db.EmployeeExpenses.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {
                "expenses.0.status": "approved",
                "expenses.0.statusReason": reason,
                "expenses.0.updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }}
        )

        # Get updated expense details
        updated_expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
        expense_details = updated_expense["expenses"][0]

        # Send email to employee
        employee_html = create_expense_email(
            status="approved",
            expense_id=expense_id,
            reason=reason
        )
        send_email(
            "samyaknahar81@gmail.com",  # Employee email
            "Expense Request Approved",
            employee_html
        )

        # Send confirmation to admin
        admin_html = f"""
        <html>
        <body>
            <h2>Expense Approval Confirmation</h2>
            <p>You have approved expense {expense_id}</p>
            <p><strong>Amount:</strong> ₹{expense_details['amount']}</p>
            <p><strong>Employee:</strong> {updated_expense['employeeId']}</p>
            <p><strong>AI Analysis:</strong> {expense_details['aiSummary']}</p>
            <p><strong>Fraud Score:</strong> {expense_details['fraudScore']}</p>
            {f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""}
        </body>
        </html>
        """
        send_email(
            "samyaknahar004@gmail.com",  # Admin email
            f"Expense {expense_id} Approved",
            admin_html
        )

        return {"status": "success", "message": "Expense approved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/{expense_id}/reject")
async def reject_expense(expense_id: str, reason: str = Form(...)):
    try:
        # Convert string ID to ObjectId
        expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        # Update expense status
        db.EmployeeExpenses.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {
                "expenses.0.status": "rejected",
                "expenses.0.statusReason": reason,
                "expenses.0.updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }}
        )

        # Get updated expense details
        updated_expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
        expense_details = updated_expense["expenses"][0]

        # Send email to employee
        employee_html = create_expense_email(
            status="rejected",
            expense_id=expense_id,
            reason=reason
        )
        send_email(
            "samyaknahar81@gmail.com",  # Employee email
            "Expense Request Rejected",
            employee_html
        )

        # Send confirmation to admin
        admin_html = f"""
        <html>
        <body>
            <h2>Expense Rejection Confirmation</h2>
            <p>You have rejected expense {expense_id}</p>
            <p><strong>Amount:</strong> ₹{expense_details['amount']}</p>
            <p><strong>Employee:</strong> {updated_expense['employeeId']}</p>
            <p><strong>AI Analysis:</strong> {expense_details['aiSummary']}</p>
            <p><strong>Fraud Score:</strong> {expense_details['fraudScore']}</p>
            <p><strong>Rejection Reason:</strong> {reason}</p>
        </body>
        </html>
        """
        send_email(
            "samyaknahar004@gmail.com",  # Admin email
            f"Expense {expense_id} Rejected",
            admin_html
        )

        return {"status": "success", "message": "Expense rejected successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
