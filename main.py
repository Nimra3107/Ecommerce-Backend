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

app = FastAPI()

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ecommerce-frontend-lac-tau.vercel.app"],
    allow_credentials=True,  #Frontend ko credentials ke saath requests karne ki permission do.
    allow_methods=["*"],    #Allow all the HTTP methods get,post,put,delete
    allow_headers=["*"],
)

# Get all products
@app.get("/products")
def get_products():
    response = (
        supabase
        .table("products")
        .select("*")
        .order("id", desc=False)
        .execute()
    )

    return response.data

#Update product quantity
@app.patch("/products/{product_id}/stock")
def update_product_stock(product_id: int, quantity_change: int):

    response = (
        supabase
        .table("products")
        .select("quantity")
        .eq("id", product_id)
        .single()
        .execute()
    )

    product = response.data

    if not product:
        return {
            "message": "Product not found"
        }

    current_quantity = product["quantity"]

    new_quantity = current_quantity + quantity_change

    if new_quantity < 0:
        return {
            "message": "Not enough stock"
        }

    update_response = (
        supabase
        .table("products")
        .update({
            "quantity": new_quantity
        })
        .eq("id", product_id)
        .execute()
    )

    return {
        "message": "Stock updated successfully",
        "product_id": product_id,
        "quantity": new_quantity
    }

#Add orders to supabase
class OrderItem(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    total_price: float


class Order(BaseModel):
    user_id: int
    customer_name: str
    address: str
    phone: str
    payment_method: str
    total_price: float
    items: list[OrderItem]


@app.post("/orders")
def create_order(order: Order):

    order_response = (
        supabase
        .table("orders")
        .insert({
            "user_id": order.user_id,
            "customer_name": order.customer_name,
            "address": order.address,
            "phone": order.phone,
            "payment_method": order.payment_method,
            "total_price": order.total_price,
            "status": "Pending"
        })
        .execute()
    )

    print("ORDER RESPONSE:", order_response)

    if not order_response.data:
        return {
            "message": "Order could not be created"
        }

    created_order = order_response.data[0]  #first recent added data
    order_id = created_order["id"]  #link the order and order-item

    order_items = [] 

    for item in order.items:
        order_items.append({
            "order_id": order_id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "price": item.price,
            "quantity": item.quantity,
            "total_price": item.total_price
        })

    print("ORDER ITEMS:", order_items)

    items_response = (
        supabase
        .table("order_items")
        .insert(order_items)
        .execute()
    )

    print("ITEMS RESPONSE:", items_response)

    if not items_response.data:
        return {
            "message": "Order created but order items could not be saved"
        }

    return {
        "message": "Order placed successfully",
        "order_id": order_id
    }

#add product to supabase
@app.post("/products")
async def add_product( 
    name: str = Form(...),   #Form(...) is used because your product request is sending both normal text/number data AND an image file.
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    image: UploadFile = File(...)
):

    # 1. Create unique image name
    file_name = f"{uuid.uuid4()}-{image.filename}"

    # 2. Read image file
    image_data = await image.read()

    # 3. Upload image to Supabase Storage
    upload_response = (
        supabase
        .storage
        .from_("product-images")
        .upload(
            file_name,
            image_data,
            {
                "content-type": image.content_type
            }
        )
    )

    # 4. Get public image URL
    image_url = (
        supabase
        .storage
        .from_("product-images")
        .get_public_url(file_name)
    )

    # 5. Insert product into products table
    product_response = (
        supabase
        .table("products")
        .insert({
            "name": name,
            "description": description,
            "category": category,
            "image": image_url,
            "price": price,
            "quantity": quantity
        })
        .execute()
    )

    # 6. Check if product was created
    if not product_response.data:
        return {
            "message": "Product could not be added"
        }

    # 7. Return response
    return {
        "message": "Product added successfully",
        "product": product_response.data[0]
    }

#Register user 
from pydantic import BaseModel

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
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

#Login user 
class LoginUser(BaseModel):
    email: str
    password: str

@app.post("/login")
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

#Get my Orders 
@app.get("/orders/user/{user_id}")
def get_user_orders(user_id: int):

    # Get all orders of this user
    orders_response = (
        supabase
        .table("orders")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    orders = orders_response.data

    # If user has no orders
    if not orders:
        return []

    result = []    

    # Get items for each order
    for order in orders:

        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq("order_id", order["id"])
            .execute()
        )

        order["items"] = items_response.data

        result.append(order)

    return result

#admin order page status
@app.get("/admin/orders")
def get_all_orders():

    # Get all orders
    orders_response = (
        supabase
        .table("orders")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    orders = orders_response.data

    if not orders:
        return []

    result = []

    # Get products for every order
    for order in orders:

        items_response = (
            supabase
            .table("order_items")
            .select("*")
            .eq("order_id", order["id"])
            .execute()
        )

        order["items"] = items_response.data

        result.append(order)

    return result


class OrderStatusUpdate(BaseModel):
    status: str


@app.patch("/admin/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate
):

    allowed_statuses = [
        "Pending",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    if status_data.status not in allowed_statuses:
        return {
            "message": "Invalid order status"
        }

    response = (
        supabase
        .table("orders")
        .update({
            "status": status_data.status
        })
        .eq("id", order_id)
        .execute()
    )

    if not response.data:
        return {
            "message": "Order not found"
        }

    return {
        "message": "Order status updated successfully",
        "order": response.data[0]
    }


# Sequence matter
# .select() → return the inserted row.
# .single() → expect exactly one row.
# .execute() → finally send/execute the complete query.


#run server in gitbash
#python -m uvicorn main:app --reload