from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from core.db import get_db, get_session
from core.config import settings
from models.user.user import User
from sqlalchemy.orm import Session
from schema.user import UserBase, NewUser, Token
from pydantic import EmailStr

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not user.check_password(password):
        return False
    return user


def create_access_token(*, data: dict):
    """
    生成JWT token
    """
    to_encode = data.copy()
    # 设置token过期时间
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY)
    return encoded_jwt


def get_user(email):
    """
    查询用户
    """
    db = get_session()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前登陆用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_user(email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    校验用户是否被激活
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@user_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    获取token
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/get_user_info/{email}", response_model=UserBase)
def get_user_info(email: EmailStr, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    获取用户信息
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserBase(email=user.email, is_active=user.is_active, full_name=user.full_name)
    else:
        raise HTTPException(status_code=400, detail="用户不存在!!!")


@user_router.put("/create_user/", response_model=UserBase)
def create_user(user: NewUser, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    创建新用户
    """
    old_user = db.query(User).filter(User.email == user.email).first()
    if old_user:
        raise HTTPException(status_code=400, detail="要创建的用户已经存在!!!")
    new_user = User()
    new_user.email = user.email
    new_user.full_name = user.full_name
    new_user.is_active = user.is_active
    new_user.convert_pass_to_hash(user.password)
    db.add(new_user)
    db.commit()
    return user
