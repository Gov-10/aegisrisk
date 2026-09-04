from pydantic import BaseModel
class RegisterSchema(BaseModel):
    name: str
    email:str
    username:str
    password: str
    user_id: str

class VerifySchema(BaseModel):
    email:str
    verify_otp:str

class LoginSchema(BaseModel):
    username:str
    password:str


