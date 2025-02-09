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
        # Test connection
        client.admin.command('ping')
        print("MongoDB connection successful!")
        db = client.expensesDB
        
        # Initialize required collections if they don't exist
        if "DepartmentsEmployees" not in db.list_collection_names():
            db.create_collection("DepartmentsEmployees")
            # Insert initial data
            db.DepartmentsEmployees.insert_many([
                {
                    "departmentId": "DEP001",
                    "employees": [{"id": "EMP001"}]
                },
                {
                    "departmentId": "DEP002",
                    "employees": [{"id": "EMP002"}]
                },
                {
                    "departmentId": "DEP003",
                    "employees": [{"id": "EMP003"}]
                },
                {
                    "departmentId": "DEP004",
                    "employees": [{"id": "EMP004"}]
                },
                {
                    "departmentId": "DEP005",
                    "employees": [{"id": "EMP005"}]
                }
            ])
        
        if "EmployeeExpenses" not in db.list_collection_names():
            db.create_collection("EmployeeExpenses")
            
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
