from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

#Get my Orders 
@router.get("/orders/user/{user_id}")
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
