from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

#Update product quantity
@router.patch("/products/{product_id}/stock")
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

