from pydantic import BaseModel, EmailStr, Field

class VendorPayloadValidation(BaseModel):
    user_email : EmailStr = Field(..., description="Use official email")
    first_name : str = Field(..., min_length=1)
    last_name : str = Field(..., min_length=1)
    age : int = Field(..., gt=17)
    plan_cost : float = Field(..., gt=0)


