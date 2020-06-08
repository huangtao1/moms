from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from apis.apis import api_router

# 初始化app实例
app = FastAPI(title=settings.APP_NAME, openapi_url=f"{settings.API_PREFIX}/openapi.json")
# 设置cors站点
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(CORSMiddleware,
                       allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"],
                       )
# 路由注册
app.include_router(api_router, prefix=settings.API_PREFIX)
