from pymongo import MongoClient
from pymongo.server_api import ServerApi

def init_mongodb():
    # MongoDB connection
    uri = "mongodb+srv://nehacodes1415:1234@cluster0.ocojt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.expensesDB

    # Drop existing collections if they exist
    existing_collections = db.list_collection_names()
    for collection in existing_collections:
        db[collection].drop()

    # Create ManagersDepartments collection with schema validation
    db.create_collection("ManagersDepartments", 
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "managerId": { "bsonType": "string" },
                    "managerName": { "bsonType": "string" },
                    "managerEmail": { "bsonType": "string" },
                    "departmentId": { "bsonType": "string" },
                    "departmentName": { "bsonType": "string" }
                }
            }
        }
    )

    # Create DepartmentsEmployees collection with schema validation
    db.create_collection("DepartmentsEmployees", 
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "departmentId": { "bsonType": "string" },
                    "departmentName": { "bsonType": "string" },
                    "employees": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "employeeId": { "bsonType": "string" },
                                "employeeName": { "bsonType": "string" },
                                "employeeEmail": { "bsonType": "string" },
                                "role": { "bsonType": "string" }
                            }
                        }
                    }
                }
            }
        }
    )

    # Create EmployeeExpenses collection with schema validation
    db.create_collection("EmployeeExpenses", 
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "employeeId": { "bsonType": "string" },
                    "departmentId": { "bsonType": "string" },
                    "expenses": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "expenseId": { "bsonType": "string" },
                                "expenseType": { "bsonType": "string" },
                                "amount": { "bsonType": "double" },
                                "date": { "bsonType": "string" },
                                "vendor": { "bsonType": "string" },
                                "description": { "bsonType": "string" },
                                "categories": { "bsonType": "array", "items": { "bsonType": "string" } },
                                "receiptImage": { "bsonType": "string" },
                                "item_details": {
                                    "bsonType": "array",
                                    "items": {
                                        "bsonType": "object",
                                        "properties": {
                                            "item": { "bsonType": "string" },
                                            "amount": { "bsonType": "double" }
                                        }
                                    }
                                },
                                "aiSummary": { "bsonType": "string" },
                                "status": { "bsonType": "string" },
                                "submittedDate": { "bsonType": "string" },
                                "approvedBy": { "bsonType": "string" },
                                "approvalDate": { "bsonType": "string" },
                                "rejectionReason": { "bsonType": "string" },
                                "fraudScore": { "bsonType": "double" },
                                "isAnomaly": { "bsonType": "bool" },
                                "createdAt": { "bsonType": "string" },
                                "updatedAt": { "bsonType": "string" }
                            }
                        }
                    }
                }
            }
        }
    )

    # Create Policies collection with schema validation
    db.create_collection("Policies", 
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "policyId": { "bsonType": "string" },
                    "policyName": { "bsonType": "string" },
                    "maxAnnualSpend": { "bsonType": "double" },
                    "maxMonthlySpend": { "bsonType": "double" },
                    "maxPerExpenseSpend": { "bsonType": "double" },
                    "allowedExpenseTypes": {
                        "bsonType": "array",
                        "items": { "bsonType": "string" }
                    },
                    "effectiveDate": { "bsonType": "string" },
                    "description": { "bsonType": "string" }
                }
            }
        }
    )

    print("Collections created successfully!")

    # Optional: Create indexes for better query performance
    db.ManagersDepartments.create_index("managerId", unique=True)
    db.ManagersDepartments.create_index("departmentId")
    db.DepartmentsEmployees.create_index("departmentId", unique=True)
    db.EmployeeExpenses.create_index("employeeId")
    db.EmployeeExpenses.create_index("departmentId")
    db.Policies.create_index("policyId", unique=True)

    print("Indexes created successfully!")

if __name__ == "__main__":
    try:
        init_mongodb()
        print("MongoDB initialization completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
