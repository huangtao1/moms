from models.base import Base
from sqlalchemy import Column, Integer, String, Boolean
from passlib.context import CryptContext

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), nullable=False)
    full_name = Column(String(200), index=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean(), default=True)

    def convert_pass_to_hash(self, password):
        self.hashed_password = pwd_context.hash(password)

    def check_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    def __repr__(self):
        return f"<User(username={self.username},email={self.email})>"
