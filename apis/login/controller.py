from fastapi import APIRouter

login_router = APIRouter()


@login_router.get("/first_login")
def first_login():
    return {"message": "hi"}
