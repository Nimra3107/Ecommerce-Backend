from fastapi import APIRouter
from supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

#admin order page status
@router.get("/admin/orders")
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


@router.patch("/admin/orders/{order_id}/status")
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