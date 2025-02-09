from pydantic import BaseModel
from typing import List, Optional

class ItemDetail(BaseModel):
    item: str
    amount: float

class ExpenseCreate(BaseModel):
    employeeId: str
    departmentId: str
    expenseType: str
    description: str
    receipt_image: str  # Now expects Cloudinary URL
    vendor: Optional[str] = None
    bill_number: Optional[str] = None
    categories: List[str]
    content_type: str = "image/url"  # Default to URL type
