from fastapi import APIRouter
from supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

class LoginUser(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(user: LoginUser):

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("email", user.email)
        .eq("password", user.password)
        .single()
        .execute()
    )

    if not response.data:
        return {
            "message": "Invalid email or password"
        }

    return response.data
