import secrets
from pydantic import BaseSettings, AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    APP_NAME = "moms"
    # api前缀
    API_PREFIX = "/api"
    # 生成随机的密钥给jwt使用
    SECRET_KEY = secrets.token_urlsafe(32)
    # token过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
    # 系统URL
    SERVER_URL: AnyHttpUrl = None
    # 跨域白名单
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    # db配置
    DB_HOST = "10.34.8.242"
    DB_PORT = 3306
    DB_DATABASE = "moms"
    DB_USER = "moms"
    DB_PASSWORD = "moms@123"
    DB_URL = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"


settings = Settings()
