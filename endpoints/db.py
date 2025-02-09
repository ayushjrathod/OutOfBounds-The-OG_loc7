from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def get_database():
    try:
        uri = os.getenv('MONGO_URL_prathamesh')
        if not uri:
            raise ValueError("MongoDB URI not found in environment variables")
            
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("MongoDB connection successful!")
        db = client.expensesDB
        
        # Initialize required collections and data
        if "DepartmentsEmployees" not in db.list_collection_names():
            print("Creating DepartmentsEmployees collection...")
            # Drop existing collection if any
            db.DepartmentsEmployees.drop()
            
            # Insert initial data
            result = db.DepartmentsEmployees.insert_many([
                {
                    "departmentId": "DEP001",
                    "departmentName": "Sales",
                    "employees": [{"id": "EMP001", "name": "Employee 1"}]
                },
                {
                    "departmentId": "DEP002",
                    "departmentName": "Finance",
                    "employees": [{"id": "EMP002", "name": "Employee 2"}]
                },
                {
                    "departmentId": "DEP003",
                    "departmentName": "Human Resources",
                    "employees": [{"id": "EMP003", "name": "Employee 3"}]
                },
                {
                    "departmentId": "DEP004",
                    "departmentName": "Research",
                    "employees": [{"id": "EMP004", "name": "Employee 4"}]
                },
                {
                    "departmentId": "DEP005",
                    "departmentName": "Information Technology",
                    "employees": [{"id": "EMP005", "name": "Employee 5"}]
                }
            ])
            print(f"Inserted {len(result.inserted_ids)} department records")
            
            # Create indexes
            db.DepartmentsEmployees.create_index("departmentId", unique=True)
            db.DepartmentsEmployees.create_index([("employees.id", 1)])
        
        if "EmployeeExpenses" not in db.list_collection_names():
            print("Creating EmployeeExpenses collection...")
            db.create_collection("EmployeeExpenses")
            db.EmployeeExpenses.create_index([("employeeId", 1)])
            db.EmployeeExpenses.create_index([("expenses.expenseId", 1)])
            
        return db
        
    except Exception as e:
        print(f"MongoDB connection error: {str(e)}")
        raise

# Create a singleton database instance
try:
    db = get_database()
except Exception as e:
    print(f"Failed to initialize database: {str(e)}")
    db = None
