import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Minimum 6 characters password")
    full_name: str = Field(default="", description="Student full name")
    is_test: bool = Field(default=False, description="Flag indicating transient test account")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserAuthRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserAuthRead
