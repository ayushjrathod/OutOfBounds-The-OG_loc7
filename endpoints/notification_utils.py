from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

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

def create_expense_email(status: str, expense_id: str, reason: Optional[str] = None) -> str:
    template = {
        "pending": {
            "subject": "Expense Request Received",
            "title": "Expense Request Acknowledgment",
            "message": f"Your expense request ({expense_id}) has been received and is being processed.",
            "color": "#007bff"
        },
        "approved": {
            "subject": "Expense Request Approved",
            "title": "Expense Request Approved",
            "message": f"Your expense request ({expense_id}) has been approved.",
            "color": "#28a745"
        },
        "rejected": {
            "subject": "Expense Request Rejected",
            "title": "Expense Request Rejected",
            "message": f"Your expense request ({expense_id}) has been rejected.",
            "color": "#dc3545"
        }
    }[status.lower()]

    reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            .header {{ background-color: {template['color']}; color: white; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{template['title']}</h1>
            </div>
            <div class="content">
                <p>{template['message']}</p>
                {reason_text}
            </div>
            <div class="footer">
                <p>Best regards,<br>Finance Department</p>
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
