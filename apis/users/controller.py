from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from core.db import get_db, get_session
from core.config import settings
from models.user.user import User
from sqlalchemy.orm import Session
from schema.user import UserBase, NewUser, Token

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def authenticate_user(username: str, password: str):
    user = get_user(username)
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


def get_user(username):
    """
    查询用户
    """
    db = get_session()
    user = db.query(User).filter(User.username == username).first()
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
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_user(username)
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
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/get_user_info/{username}", response_model=UserBase)
def get_user_info(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    获取用户信息
    定义depends current_user是为了验证是否已经获取登录的token
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        return UserBase(username=user.username, email=user.email, is_active=user.is_active, full_name=user.full_name)
    else:
        raise HTTPException(status_code=400, detail="用户不存在!!!")


@user_router.put("/create_user/", response_model=UserBase,
                 responses={400: {"description": "要创建的用户已经存在"}, 201: {"description": "用户创建成功"}})
def create_user(user: NewUser, response: Response, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    创建新用户
    """
    old_user = db.query(User).filter(User.username == user.username).first()
    if old_user:
        raise HTTPException(status_code=400, detail="要创建的用户已经存在!!!")
    user_dict = {"username": user.username, "email": user.email, "full_name": user.full_name,
                 "is_active": user.is_active}
    new_user = User(**user_dict)
    new_user.convert_pass_to_hash(user.password)
    db.add(new_user)
    db.commit()
    response.status_code = status.HTTP_201_CREATED
    return UserBase(**user_dict)
