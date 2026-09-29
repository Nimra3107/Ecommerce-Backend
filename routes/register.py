from fastapi import APIRouter
from supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register(user: RegisterUser):

    response = (
        supabase
        .table("users")
        .insert({
            "username": user.username,
            "email": user.email,
            "password": user.password
        })
        .select() #Insert this data, and return the inserted row back to me.
        .single()  #Returns exactly one row from the database.
        .execute()  #Executes the query and sends it to the database.
    )

    return response.data
