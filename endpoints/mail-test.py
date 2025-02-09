from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email configuration
SENDER_EMAIL = "samyaknahar81@gmail.com"
SENDER_PASSWORD = "mufy nwhg fgdl vsou"

# Pydantic models for request validation
class InitiationRequest(BaseModel):
    receiver_email: EmailStr
    code: str

class StatusRequest(BaseModel):
    receiver_email: EmailStr
    code: str
    status: str
    reason: Optional[str] = None

def send_email(receiver_email: str, subject: str, html_content: str):
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email.strip()
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, receiver_email.strip(), text)
            return True, "Email sent successfully!"

    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def create_initiation_email(code: str):
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            .header {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reimbursement Request Acknowledgment</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Your reimbursement request with code <strong>{code}</strong> has been acknowledged. Please wait 2-3 business days for further information.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>Your Company</p>
            </div>
        </div>
    </body>
    </html>
    """

def create_status_email(status: str, code: str, reason: Optional[str] = None):
    if status not in ["accepted", "declined"]:
        raise ValueError("Invalid status. Use 'accepted' or 'declined'.")
    
    message = f"Your reimbursement request with code <strong>{code}</strong> has been {status}."
    reason_text = f"<p>Reason: {reason}</p>" if reason and status == "declined" else ""

    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
            .header {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ background-color: #f8f9fa; padding: 10px; text-align: center; border-radius: 0 0 10px 10px; }}
            .status-accepted {{ color: #28a745; }}
            .status-declined {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Reimbursement Request Status</h1>
            </div>
            <div class="content">
                <p class="status-{status}">{message}</p>
                {reason_text}
            </div>
            <div class="footer">
                <p>Best regards,<br>Your Company</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/send-initiation-email")
async def send_initiation_email(request: InitiationRequest):
    html_content = create_initiation_email(request.code)
    success, message = send_email(
        request.receiver_email,
        "Reimbursement Request Acknowledgment",
        html_content
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {"status": "success", "message": message}

@app.post("/send-status-email")
async def send_status_email(request: StatusRequest):
    try:
        html_content = create_status_email(request.status, request.code, request.reason)
        success, message = send_email(
            request.receiver_email,
            "Reimbursement Request Status",
            html_content
        )
        
        if not success:
            raise HTTPException(status_code=500, detail=message)
        
        return {"status": "success", "message": message}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)