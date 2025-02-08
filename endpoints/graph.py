from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
uri = "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.expensesDB

@app.get("/api/analytics/department-expenses")
async def get_department_expenses():
    """Get total expenses by department"""
    pipeline = [
        {
            "$unwind": "$expenses"
        },
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
        {
            "$unwind": "$expenses"
        },
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
        {
            "$sort": {"_id.year": 1, "_id.month": 1}
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/category-distribution")
async def get_category_distribution():
    """Get expense distribution by category"""
    pipeline = [
        {
            "$unwind": "$expenses"
        },
        {
            "$unwind": "$expenses.categories"
        },
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
        {
            "$unwind": "$expenses"
        },
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
        {
            "$unwind": "$expenses"
        },
        {
            "$group": {
                "_id": "$expenses.vendor",
                "total_amount": {"$sum": "$expenses.amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_amount": -1}
        },
        {
            "$limit": 10
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/employee-expenses")
async def get_employee_expenses():
    """Get total expenses by employee"""
    pipeline = [
        {
            "$unwind": "$expenses"
        },
        {
            "$group": {
                "_id": "$employeeId",
                "total_amount": {"$sum": "$expenses.amount"},
                "transaction_count": {"$sum": 1},
                "avg_amount": {"$avg": "$expenses.amount"},
                "departments": {"$addToSet": "$departmentId"}
            }
        },
        {
            "$sort": {"total_amount": -1}
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

@app.get("/api/analytics/employee-categories")
async def get_employee_categories():
    """Get category-wise spending for each employee"""
    pipeline = [
        {
            "$unwind": "$expenses"
        },
        {
            "$unwind": "$expenses.categories"
        },
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
        {
            "$sort": {"total_amount": -1}
        }
    ]
    result = list(db.EmployeeExpenses.aggregate(pipeline))
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
