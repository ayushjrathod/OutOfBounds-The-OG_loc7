from pymongo import MongoClient
from pymongo.server_api import ServerApi
import random
from datetime import datetime, timedelta
import uuid
import base64

# MongoDB connection
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

expense_categories = [
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

vendors = {
    "Travel Expenses": ["MakeMyTrip", "Cleartrip", "IRCTC", "Uber", "Ola"],
    "Work Equipment & Supplies": ["Amazon", "Flipkart", "Office Depot", "Staples", "Best Buy"],
    "Meals & Entertainment": ["Taj Hotels", "McDonald's", "Starbucks", "PVR Cinemas", "Zomato"],
    "Internet & Phone Bills": ["Airtel", "Jio", "Vi", "BSNL", "ACT Fibernet"],
    "Professional Development": ["Udemy", "Coursera", "LinkedIn Learning", "Skillshare", "Pluralsight"],
    "Health & Wellness": ["Cult.fit", "Apollo Pharmacy", "Practo", "HealthifyMe", "Fitbit"],
    "Commuting Expenses": ["Metro Card", "Bus Pass", "Parking Services", "Fuel Stations", "Local Transport"],
    "Software & Subscriptions": ["Microsoft", "Adobe", "Zoom", "Slack", "AWS"],
    "Relocation Assistance": ["Packers & Movers", "Housing.com", "NoBroker", "Urban Company", "HomeServices"],
    "Client & Marketing Expenses": ["Facebook Ads", "Google Ads", "Event Management", "Print Media", "Digital Marketing"]
}

def generate_expenses(employee_id, dept_id, start_date, end_date):
    expenses = []
    current_date = start_date

    while current_date <= end_date:
        # Generate 2-4 expenses per month
        for _ in range(random.randint(2, 4)):
            category = random.choice(expense_categories)
            vendor = random.choice(vendors[category])
            
            # Generate realistic amounts based on category
            amount_ranges = {
                "Travel Expenses": (2000, 15000),
                "Work Equipment & Supplies": (1000, 8000),
                "Meals & Entertainment": (500, 3000),
                "Internet & Phone Bills": (999, 2499),
                "Professional Development": (2000, 20000),
                "Health & Wellness": (1000, 5000),
                "Commuting Expenses": (500, 3000),
                "Software & Subscriptions": (399, 4999),
                "Relocation Assistance": (5000, 25000),
                "Client & Marketing Expenses": (2000, 15000)
            }

            amount = round(random.uniform(*amount_ranges[category]), 2)
            
            # Generate realistic items based on category
            items = []
            if category == "Travel Expenses":
                items = [
                    {"item": "Flight Ticket", "amount": amount * 0.6},
                    {"item": "Hotel Stay", "amount": amount * 0.3},
                    {"item": "Local Transport", "amount": amount * 0.1}
                ]
            elif category == "Meals & Entertainment":
                items = [
                    {"item": "Team Lunch", "amount": amount * 0.7},
                    {"item": "Beverages", "amount": amount * 0.3}
                ]
            else:
                items = [{"item": category, "amount": amount}]

            expense = {
                "expenseId": str(uuid.uuid4()),
                "expenseType": category,
                "amount": amount,
                "date": current_date.strftime("%Y-%m-%d"),
                "vendor": vendor,
                "description": f"{category} - {vendor}",
                "categories": [category],
                "receiptImage": "base64_placeholder",  # In real scenario, this would be actual receipt image
                "item_details": items,
                "aiSummary": f"Expense for {category} at {vendor}",
                "status": random.choice(["Approved", "Pending", "Rejected"]),
                "submittedDate": current_date.strftime("%Y-%m-%d"),
                "approvedBy": "MGR001",
                "approvalDate": (current_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "rejectionReason": None,
                "fraudScore": round(random.uniform(0, 1), 2),
                "isAnomaly": random.random() < 0.1,  # 10% chance of being anomaly
                "createdAt": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                "updatedAt": current_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            expenses.append(expense)
        
        # Move to next month
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=random.randint(1, 28))

    return expenses

def seed_database():
    try:
        # Clear existing data
        db.ManagersDepartments.delete_many({})
        db.DepartmentsEmployees.delete_many({})
        db.EmployeeExpenses.delete_many({})

        # Create managers and departments
        for dept in departments:
            manager_id = f"MGR{dept['id'][3:]}"
            db.ManagersDepartments.insert_one({
                "managerId": manager_id,
                "managerName": f"Manager {dept['name']}",
                "managerEmail": f"manager.{dept['name'].lower()}@company.com",
                "departmentId": dept['id'],
                "departmentName": dept['name']
            })

        # Create departments and employees
        for dept in departments:
            dept_employees = [emp for emp in employees if emp['dept_id'] == dept['id']]
            db.DepartmentsEmployees.insert_one({
                "departmentId": dept['id'],
                "departmentName": dept['name'],
                "employees": dept_employees
            })

        # Create employee expenses
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 2, 29)

        for employee in employees:
            expenses = generate_expenses(employee['id'], employee['dept_id'], start_date, end_date)
            db.EmployeeExpenses.insert_one({
                "employeeId": employee['id'],
                "departmentId": employee['dept_id'],
                "expenses": expenses
            })

        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {str(e)}")

if __name__ == "__main__":
    seed_database()
