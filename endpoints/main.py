from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from db import db
from models import ExpenseCreate, EmailRequest, ApprovalRequest
from utils import process_expense
import os
from dotenv import load_dotenv
from google import genai
from datetime import datetime
from pymongo import MongoClient  # Add this import
from pymongo.server_api import ServerApi  # Add this import
from notification_utils import send_email, create_expense_notification_email
from typing import Dict, Any
from bson import ObjectId

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

# Verify database connection at startup
@app.on_event("startup")
async def startup_event():
    try:
        # Test the connection with proper MongoDB command
        db.command("ping")
        print("Database connection verified during startup")
    except Exception as e:
        print(f"Database connection error during startup: {str(e)}")
        raise Exception("Database connection failed during startup check") from e

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

@app.post("/api/expenses/")
async def create_expense(
    employeeId: str = Form(...),
    departmentId: str = Form(...),
    expenseType: str = Form(...),
    description: str = Form(...),
    vendor: str = Form(None),
    categories: str = Form(...),
    receiptImage: str = Form(...)  # Changed to accept Cloudinary URL
):
    try:
        # Initialize fresh DB connection for this request
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

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
            print("Executing query:", query)
            department_employee = db.DepartmentsEmployees.find_one(query)
            print("Query result:", department_employee)
            
            if not department_employee:
                # Try to find if department and employee exist separately
                dept = db.DepartmentsEmployees.find_one({"departmentId": departmentId})
                if not dept:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Department {departmentId} does not exist"
                    )
                
                emp_exists = db.DepartmentsEmployees.find_one(
                    {"employees.id": employeeId}
                )
                if not emp_exists:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Employee {employeeId} does not exist"
                    )
                
                raise HTTPException(
                    status_code=400,
                    detail=f"Employee {employeeId} is not associated with department {departmentId}"
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Database query error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error validating employee and department relationship"
            )

        # Convert categories string into list (could be single or multiple)
        if ',' in categories:
            categories_list = [cat.strip() for cat in categories.split(',')]
        else:
            categories_list = [categories.strip()]

        # Validate each category
        for cat in categories_list:
            if cat not in VALID_EXPENSE_CATEGORIES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category: {cat}. Must be one of: {', '.join(VALID_EXPENSE_CATEGORIES)}"
                )

        # Process and store the expense
        expense = ExpenseCreate(
            employeeId=employeeId,
            departmentId=departmentId,
            expenseType=expenseType,
            description=description,
            vendor=vendor,
            categories=categories_list,
            receipt_image=receiptImage,
            content_type="image/url"
        )
        
        # Process expense
        try:
            result = process_expense(expense, db)
            stored_expense = db.EmployeeExpenses.find_one({"_id": result.inserted_id})
            if not stored_expense or "expenses" not in stored_expense:
                raise ValueError("Failed to store expense properly")
                
            # Send notification to employee
            employee_html = create_expense_notification_email(
                expense_data=stored_expense,
                notification_type="submission"
            )
            
            emp_success, emp_message = send_email(
                "samyaknahar81@gmail.com",  # Employee email
                "Expense Submission Confirmation",
                employee_html
            )

            # Send detailed notification to admin
            admin_html = f"""
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ padding: 20px; }}
        .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .amount {{ font-size: 24px; color: #28a745; font-weight: bold; }}
        .warning {{ background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .action-needed {{ background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center; }}
        .footer {{ text-align: center; padding: 20px; color: #6c757d; }}
        .button {{ display: inline-block; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧾 New Expense Submission</h1>
        </div>
        <div class="content">
            <div class="action-needed">
                <h2>⚠️ Action Required: Review Needed</h2>
            </div>
            
            <div class="details">
                <h3>Expense Details:</h3>
                <p><strong>Employee ID:</strong> {stored_expense['employeeId']}</p>
                <p><strong>Department:</strong> {stored_expense['departmentId']}</p>
                <p><strong>Type:</strong> {stored_expense['expenses'][0]['expenseType']}</p>
                <p><strong>Amount:</strong> <span class="amount">₹{stored_expense['expenses'][0]['amount']:,.2f}</span></p>
                <p><strong>Date:</strong> {stored_expense['expenses'][0]['date']}</p>
                <p><strong>Description:</strong> {stored_expense['expenses'][0]['description']}</p>
                <p><strong>Categories:</strong> {', '.join(stored_expense['expenses'][0]['categories'])}</p>
            </div>

            {'''<div class="warning">
                <h3>AI Analysis Flagged This Expense:</h3>
                <p>{}</p>
                <p><strong>Fraud Score:</strong> {}</p>
            </div>'''.format(stored_expense['expenses'][0]['aiSummary'], stored_expense['expenses'][0]['fraudScore']) if stored_expense['expenses'][0].get('isAnomaly', False) else ''}

            <div style="text-align: center; margin-top: 20px;">
                <a href="http://localhost:3000/admin/expenses" class="button">Review Expense</a>
            </div>
        </div>
        <div class="footer">
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
            admin_success, admin_message = send_email(
                "samyaknahar004@gmail.com",  # Admin email
                f"🧾 New Expense Submission - {stored_expense['expenses'][0]['expenseType']}",
                admin_html
            )

            # If it's a high-risk expense, send an additional alert
            if stored_expense['expenses'][0].get('isAnomaly', False):
                alert_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="background-color: #ffebee; padding: 20px; border-radius: 10px;">
                            <h2 style="color: #c62828;">⚠️ High Risk Expense Detected</h2>
                            <p><strong>Amount:</strong> ₹{stored_expense['expenses'][0]['amount']:,.2f}</p>
                            <p><strong>AI Analysis:</strong> {stored_expense['expenses'][0]['aiSummary']}</p>
                            <p><strong>Fraud Score:</strong> {stored_expense['expenses'][0]['fraudScore']}</p>
                            <p><strong>Employee ID:</strong> {stored_expense['employeeId']}</p>
                        </div>
                    </body>
                </html>
                """
                
                send_email(
                    "samyaknahar004@gmail.com",
                    "🚨 High Risk Expense Alert",
                    alert_html
                )

            return {
                "status": "success",
                "expense_id": str(result.inserted_id),
                "message": "Expense processed successfully",
                "notifications": {
                    "employee": emp_success,
                    "admin": admin_success
                }
            }

        except Exception as e:
            print(f"Error processing expense: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing expense: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
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

def create_decision_email(expense: dict, decision: str, reason: str) -> str:
    status_colors = {
        "approved": "#28a745",
        "rejected": "#dc3545"
    }
    
    icons = {
        "approved": "✅",
        "rejected": "❌"
    }

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
            .header {{ 
                background-color: {status_colors[decision]}; 
                color: white; 
                padding: 30px 20px;
                text-align: center; 
                border-radius: 15px 15px 0 0;
            }}
            .icon {{ font-size: 48px; margin-bottom: 15px; }}
            .decision-badge {{
                display: inline-block;
                padding: 8px 20px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .content {{ padding: 30px; }}
            .amount-section {{
                text-align: center;
                padding: 20px;
                margin: 20px 0;
                background-color: #f8f9fa;
                border-radius: 10px;
            }}
            .amount {{ 
                font-size: 32px; 
                font-weight: bold; 
                color: {status_colors[decision]};
            }}
            .details-grid {{
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 15px;
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid {status_colors[decision]};
            }}
            .label {{ 
                font-weight: bold; 
                color: #666;
                padding-right: 20px;
            }}
            .value {{ color: #333; }}
            .reason-box {{
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid {status_colors[decision]};
            }}
            .reason-title {{
                margin: 0 0 10px 0;
                color: #444;
                font-size: 18px;
            }}
            .footer {{
                background-color: #f8f9fa;
                color: #666;
                text-align: center;
                padding: 20px;
                border-radius: 0 0 15px 15px;
                border-top: 1px solid #eee;
            }}
            .timestamp {{
                font-size: 12px;
                color: #888;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">{icons[decision]}</div>
                <div class="decision-badge">EXPENSE {decision.upper()}</div>
                <h1>Expense {decision.title()}</h1>
            </div>
            
            <div class="content">
                <div class="amount-section">
                    <div>Total Amount</div>
                    <div class="amount">₹{expense['expenses'][0]['amount']:,.2f}</div>
                </div>

                <div class="details-grid">
                    <div class="label">Expense ID:</div>
                    <div class="value">{expense['expenses'][0]['expenseId']}</div>
                    
                    <div class="label">Employee ID:</div>
                    <div class="value">{expense['employeeId']}</div>
                    
                    <div class="label">Department:</div>
                    <div class="value">{expense['departmentId']}</div>
                    
                    <div class="label">Type:</div>
                    <div class="value">{expense['expenses'][0]['expenseType']}</div>
                    
                    <div class="label">Date:</div>
                    <div class="value">{expense['expenses'][0]['date']}</div>
                    
                    <div class="label">Vendor:</div>
                    <div class="value">{expense['expenses'][0]['vendor']}</div>
                    
                    <div class="label">Categories:</div>
                    <div class="value">{', '.join(expense['expenses'][0]['categories'])}</div>
                </div>

                <div class="reason-box">
                    <h3 class="reason-title">💬 Reason for {decision.title()}:</h3>
                    <p>{reason}</p>
                </div>

                {f'''
                <div class="reason-box" style="border-color: #dc3545;">
                    <h3 class="reason-title" style="color: #dc3545;">⚠️ AI Analysis:</h3>
                    <p>{expense['expenses'][0]['aiSummary']}</p>
                </div>
                ''' if expense['expenses'][0].get('isAnomaly', False) else ''}
            </div>
            
            <div class="footer">
                <p>This is an automated message from the Finance Department</p>
                <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/api/expenses/{expense_id}/approve")
async def approve_expense(expense_id: str, request: Request):
    try:
        # Get request body
        body = await request.json()
        reason = body.get('reason')
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        # First try to find by expenseId in the expenses array
        expense = db.EmployeeExpenses.find_one({
            "expenses": {
                "$elemMatch": {
                    "expenseId": expense_id
                }
            }
        })

        if not expense:
            # If not found by expenseId, try as ObjectId
            try:
                expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
            except:
                pass

        if not expense:
            raise HTTPException(
                status_code=404,
                detail=f"Expense not found with ID: {expense_id}"
            )

        print(f"Found expense: {expense}")  # Debug print

        # Send email to employee using new template
        html_content = create_decision_email(
            expense=expense,
            decision="approved",
            reason=reason
        )
        
        emp_success, emp_message = send_email(
            "samyaknahar81@gmail.com",  # Employee email
            "Expense Request Approved",
            html_content
        )

        # Send to admin with same template
        admin_success, admin_message = send_email(
            "samyaknahar004@gmail.com",  # Admin email
            f"Expense {expense_id} Approved",
            html_content
        )

        return {
            "status": "success",
            "message": "Approval notifications sent successfully",
            "employee_email": {"success": emp_success, "message": emp_message},
            "admin_email": {"success": admin_success, "message": admin_message}
        }

    except Exception as e:
        print(f"Error in approve_expense: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expenses/{expense_id}/reject")
async def reject_expense(expense_id: str, request: Request):
    try:
        # Get request body
        body = await request.json()
        reason = body.get('reason')
        
        # Initialize MongoDB connection
        uri = os.getenv('MONGO_URL_prathamesh')
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client.expensesDB

        if not reason:
            raise HTTPException(status_code=400, detail="Reason is required for rejection")

        # First try to find by expenseId in the expenses array
        expense = db.EmployeeExpenses.find_one({
            "expenses": {
                "$elemMatch": {
                    "expenseId": expense_id
                }
            }
        })

        if not expense:
            # If not found by expenseId, try as ObjectId
            try:
                expense = db.EmployeeExpenses.find_one({"_id": ObjectId(expense_id)})
            except:
                pass

        if not expense:
            raise HTTPException(
                status_code=404,
                detail=f"Expense not found with ID: {expense_id}"
            )

        # Send email to employee using new template
        html_content = create_decision_email(
            expense=expense,
            decision="rejected",
            reason=reason
        )
        
        emp_success, emp_message = send_email(
            "samyaknahar81@gmail.com",
            "Expense Request Rejected",
            html_content
        )

        # Send to admin with same template
        admin_success, admin_message = send_email(
            "samyaknahar004@gmail.com",
            f"Expense {expense_id} Rejected",
            html_content
        )

        return {
            "status": "success",
            "message": "Rejection notifications sent successfully",
            "employee_email": {"success": emp_success, "message": emp_message},
            "admin_email": {"success": admin_success, "message": admin_message}
        }

    except Exception as e:
        print(f"Error in reject_expense: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080))
    )
