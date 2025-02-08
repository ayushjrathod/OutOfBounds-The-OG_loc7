from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection details
uri = "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.expensesDB

# Sample data
departments = [
    {"id": "DEP001", "name": "Sales"},
    {"id": "DEP002", "name": "Finance"},
    {"id": "DEP003", "name": "Human Resources"},
    {"id": "DEP004", "name": "Research"},
    {"id": "DEP005", "name": "Information Technology"}
]

employees = [
    {"id": "EMP001", "name": "John Smith", "email": "john.smith@company.com", "dept_id": "DEP001", "role": "Sales Manager"},
    {"id": "EMP002", "name": "Emma Wilson", "email": "emma.wilson@company.com", "dept_id": "DEP002", "role": "Financial Analyst"},
    {"id": "EMP003", "name": "Michael Brown", "email": "michael.brown@company.com", "dept_id": "DEP003", "role": "HR Specialist"},
    {"id": "EMP004", "name": "Sarah Johnson", "email": "sarah.johnson@company.com", "dept_id": "DEP004", "role": "Research Scientist"},
    {"id": "EMP005", "name": "David Lee", "email": "david.lee@company.com", "dept_id": "DEP005", "role": "IT Manager"}
]

# Prepare data for DepartmentsEmployees collection
departments_employees_data = []
for dept in departments:
    employees_in_dept = [
        {"id": emp["id"], "name": emp["name"], "email": emp["email"], "role": emp["role"]}
        for emp in employees if emp["dept_id"] == dept["id"]
    ]
    departments_employees_data.append({
        "departmentId": dept["id"],
        "departmentName": dept["name"],
        "employees": employees_in_dept
    })

# Insert data into DepartmentsEmployees collection
departments_employees_collection = db.DepartmentsEmployees
departments_employees_collection.insert_many(departments_employees_data)

print("Data inserted into DepartmentsEmployees collection successfully!")
