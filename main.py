# from fastapi import FastAPI
# from supabase_client import supabase

# app = FastAPI()

# @app.get("/products")
# def get_products():
#     response = supabase.table("products").select("*").execute()
#     return response.data

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uuid

from supabase_client import supabase
from pydantic import BaseModel


from routes.register import router as register_router
from routes.login import router as login_router
from routes.products import router as products_router
from routes.myorder import router as orders_router
from routes.checkout import router as checkout_router
from routes.cart import router as cart_router
from routes.adminorder import router as adminorder_router
from routes.addproduct import router as addproduct_router

app = FastAPI()

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
        "https://ecommerce-frontend-lac-tau.vercel.app"],
        # "https://ecommerce-frontend-lac-tau.vercel.app"],
    allow_credentials=True,  #Frontend ko credentials ke saath requests karne ki permission do.
    allow_methods=["*"],    #Allow all the HTTP methods get,post,put,delete
    allow_headers=["*"],
)

app.include_router(cart_router)
app.include_router(addproduct_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(checkout_router)
app.include_router(adminorder_router)
app.include_router(login_router)
app.include_router(register_router)


# Sequence matter
# .select() → return the inserted row.
# .single() → expect exactly one row.
# .execute() → finally send/execute the complete query.


#run server in gitbash
#python -m uvicorn main:app --reload