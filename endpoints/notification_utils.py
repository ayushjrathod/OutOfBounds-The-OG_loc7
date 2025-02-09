from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime  # Add this import

load_dotenv()

class EmailRequest(BaseModel):
    receiver_email: EmailStr
    code: str
    status: Optional[str] = None
    reason: Optional[str] = None

def send_email(receiver_email: str, subject: str, html_content: str) -> tuple[bool, str]:
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = os.getenv('EMAIL_SENDER')
        msg['To'] = receiver_email.strip()
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_SENDER'), os.getenv('EMAIL_APP_PASSWORD'))
            text = msg.as_string()
            server.sendmail(os.getenv('EMAIL_SENDER'), receiver_email.strip(), text)
            return True, "Email sent successfully!"

    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def create_expense_notification_email(expense_data: dict, notification_type: str, reason: str = None) -> str:
    """Create email template for different expense notifications"""
    
    expense_details = expense_data["expenses"][0]
    status_colors = {
        "pending": "#007bff",
        "approved": "#28a745",
        "rejected": "#dc3545"
    }

    templates = {
        "submission": {
            "subject": "New Expense Submission",
            "title": "Expense Submission Receipt",
            "color": status_colors["pending"],
            "icon": "📝"
        },
        "approved": {
            "subject": "Expense Approved",
            "title": "Expense Request Approved",
            "color": status_colors["approved"],
            "icon": "✅"
        },
        "rejected": {
            "subject": "Expense Rejected",
            "title": "Expense Request Rejected",
            "color": status_colors["rejected"],
            "icon": "❌"
        }
    }

    template = templates[notification_type]
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
            .header {{ 
                background-color: {template["color"]}; 
                color: white; 
                padding: 20px; 
                text-align: center; 
                border-radius: 12px 12px 0 0;
                position: relative;
            }}
            .icon {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .content {{ padding: 30px; background-color: #ffffff; }}
            .footer {{ 
                background-color: #f8f9fa; 
                padding: 20px; 
                text-align: center; 
                border-radius: 0 0 12px 12px;
                border-top: 1px solid #eee;
            }}
            .details {{ 
                margin: 20px 0; 
                padding: 20px; 
                background-color: #f8f9fa; 
                border-radius: 10px;
                border-left: 4px solid {template["color"]};
            }}
            .fraud-alert {{ 
                color: #dc3545; 
                padding: 15px; 
                border: 2px solid #dc3545; 
                border-radius: 8px; 
                margin: 15px 0;
                background-color: #fff5f5;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 15px;
                border-radius: 20px;
                background-color: {template["color"]};
                color: white;
                font-weight: bold;
                margin: 10px 0;
            }}
            .amount {{ 
                font-size: 24px; 
                font-weight: bold; 
                color: {template["color"]};
                margin: 15px 0;
            }}
            .detail-row {{
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .detail-label {{
                font-weight: bold;
                color: #666;
            }}
            .reason-box {{
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid {template["color"]};
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">{template["icon"]}</div>
                <h1>{template["title"]}</h1>
            </div>
            <div class="content">
                <div class="status-badge">{notification_type.upper()}</div>
                
                <div class="amount">
                    ₹{expense_details["amount"]:,.2f}
                </div>

                <div class="details">
                    <div class="detail-row">
                        <span class="detail-label">Expense ID:</span>
                        <span>{expense_details["expenseId"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Type:</span>
                        <span>{expense_details["expenseType"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span>{expense_details["date"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Vendor:</span>
                        <span>{expense_details["vendor"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Description:</span>
                        <span>{expense_details["description"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Categories:</span>
                        <span>{", ".join(expense_details["categories"])}</span>
                    </div>
                </div>

                {f'''<div class="fraud-alert">
                    <h3>⚠️ AI Analysis</h3>
                    <p>{expense_details["aiSummary"]}</p>
                </div>''' if expense_details["isAnomaly"] else ''}

                {f'''<div class="reason-box">
                    <h3>💬 {notification_type.title()} Reason:</h3>
                    <p>{reason}</p>
                </div>''' if reason else ''}
            </div>
            <div class="footer">
                <p>This is an automated message from the Finance Department</p>
                <small style="color: #666;">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</small>
            </div>
        </div>
    </body>
    </html>
    """

def create_admin_approval_email(expense_id: str, employee_id: str, amount: float, ai_summary: str, fraud_score: float) -> str:
    """Create email template for admin approval"""
    base_url = "http://localhost:3000/manager/expenses"
    approve_url = f"{base_url}/{expense_id}?action=approve"
    reject_url = f"{base_url}/{expense_id}?action=reject"
    
    status_color = "#dc3545" if fraud_score > 0.7 else "#28a745"
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            .header {{ background-color: #007bff; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 0 0 10px 10px; }}
            .fraud-score {{ color: {status_color}; font-weight: bold; }}
            .button {{ display: inline-block; padding: 10px 20px; margin: 10px; text-decoration: none; border-radius: 5px; color: white; text-align: center; }}
            .approve {{ background-color: #28a745; }}
            .reject {{ background-color: #dc3545; }}
            .view-details {{ background-color: #007bff; display: block; width: 200px; margin: 20px auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>New Expense Request Requires Approval</h1>
            </div>
            <div class="content">
                <p><strong>Employee ID:</strong> {employee_id}</p>
                <p><strong>Amount:</strong> ₹{amount:.2f}</p>
                <p><strong>AI Analysis:</strong> {ai_summary}</p>
                <p><strong>Fraud Score:</strong> <span class="fraud-score">{fraud_score:.2f}</span></p>
                
                <a href="{base_url}/{expense_id}" class="button view-details">View Full Details</a>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="{approve_url}" class="button approve">Approve Expense</a>
                    <a href="{reject_url}" class="button reject">Reject Expense</a>
                </div>
            </div>
            <div class="footer">
                <p>Click 'View Full Details' to see complete expense information and take action.</p>
            </div>
        </div>
    </body>
    </html>
    """
