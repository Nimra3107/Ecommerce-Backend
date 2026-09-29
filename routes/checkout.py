from fastapi import APIRouter
from supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

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


@router.post("/orders")
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
 