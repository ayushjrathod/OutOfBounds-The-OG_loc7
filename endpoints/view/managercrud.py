from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import json

app = FastAPI()

# CORS configuration
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

# Helper function to convert ObjectId to string
def serialize_object_id(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Managers & Departments APIs
@app.post("/managers-departments/")
async def create_manager_department(data: dict = Body(...)):
    result = db.ManagersDepartments.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Manager department created successfully"}

@app.get("/managers-departments/")
async def get_all_manager_departments():
    managers = list(db.ManagersDepartments.find({}, {'_id': 0}))
    return managers

@app.get("/managers-departments/{manager_id}")
async def get_manager_department(manager_id: str):
    manager = db.ManagersDepartments.find_one({"managerId": manager_id}, {'_id': 0})
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return manager

@app.put("/managers-departments/{manager_id}")
async def update_manager_department(manager_id: str, data: dict = Body(...)):
    result = db.ManagersDepartments.update_one(
        {"managerId": manager_id},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Manager not found")
    return {"message": "Manager department updated successfully"}

@app.delete("/managers-departments/{manager_id}")
async def delete_manager_department(manager_id: str):
    result = db.ManagersDepartments.delete_one({"managerId": manager_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Manager not found")
    return {"message": "Manager department deleted successfully"}

# Departments & Employees APIs
@app.post("/departments-employees/")
async def create_department_employees(data: dict = Body(...)):
    result = db.DepartmentsEmployees.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Department employees created successfully"}

@app.get("/departments-employees/")
async def get_all_department_employees():
    departments = list(db.DepartmentsEmployees.find({}, {'_id': 0}))
    return departments

@app.get("/departments-employees/{department_id}")
async def get_department_employees(department_id: str):
    department = db.DepartmentsEmployees.find_one({"departmentId": department_id}, {'_id': 0})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

@app.put("/departments-employees/{department_id}")
async def update_department_employees(department_id: str, data: dict = Body(...)):
    result = db.DepartmentsEmployees.update_one(
        {"departmentId": department_id},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"message": "Department employees updated successfully"}

@app.delete("/departments-employees/{department_id}")
async def delete_department_employees(department_id: str):
    result = db.DepartmentsEmployees.delete_one({"departmentId": department_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"message": "Department employees deleted successfully"}

# Employee Expenses APIs
@app.post("/employee-expenses/")
async def create_employee_expenses(data: dict = Body(...)):
    result = db.EmployeeExpenses.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Employee expenses created successfully"}

@app.get("/employee-expenses/")
async def get_all_employee_expenses():
    expenses = list(db.EmployeeExpenses.find({}, {'_id': 0}))
    return expenses

@app.get("/employee-expenses/{employee_id}")
async def get_employee_expenses(employee_id: str):
    expenses = db.EmployeeExpenses.find_one({"employeeId": employee_id}, {'_id': 0})
    if not expenses:
        raise HTTPException(status_code=404, detail="Employee expenses not found")
    return expenses

@app.put("/employee-expenses/{employee_id}")
async def update_employee_expenses(employee_id: str, data: dict = Body(...)):
    result = db.EmployeeExpenses.update_one(
        {"employeeId": employee_id},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Employee expenses not found")
    return {"message": "Employee expenses updated successfully"}

@app.delete("/employee-expenses/{employee_id}")
async def delete_employee_expenses(employee_id: str):
    result = db.EmployeeExpenses.delete_one({"employeeId": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee expenses not found")
    return {"message": "Employee expenses deleted successfully"}

# Policies APIs
@app.post("/policies/")
async def create_policy(data: dict = Body(...)):
    result = db.Policies.insert_one(data)
    return {"id": str(result.inserted_id), "message": "Policy created successfully"}

@app.get("/policies/")
async def get_all_policies():
    policies = list(db.Policies.find({}, {'_id': 0}))
    return policies

@app.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    policy = db.Policies.find_one({"policyId": policy_id}, {'_id': 0})
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@app.put("/policies/{policy_id}")
async def update_policy(policy_id: str, data: dict = Body(...)):
    result = db.Policies.update_one(
        {"policyId": policy_id},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy updated successfully"}

@app.delete("/policies/{policy_id}")
async def delete_policy(policy_id: str):
    result = db.Policies.delete_one({"policyId": policy_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)