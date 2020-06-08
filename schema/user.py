from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "huangtao123689@gmail.com",
                "password": "123456"
            }
        }


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    full_name: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "email": "huangtao123689@gmail.com",
                "is_active": True,
                "full_name": "huangtao"
            }
        }


class NewUser(UserBase):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "huangtao123689@gmail.com",
                "is_active": True,
                "full_name": "huangtao",
                "password": "123456"
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str
