from fastapi import APIRouter
from supabase_client import supabase

router = APIRouter()

@router.get("/products")
def get_products():

    products_response = (
        supabase
        .table("products")
        .select("*")
        .order("id", desc=False)
        .execute()
    )

    categories_response = (
        supabase
        .table("categories")
        .select("*")
        .execute()
    )

    categories = categories_response.data

    for product in products_response.data:
        category = next(
            (
                category   #store the matching category whose match with category_id
                for category in categories
                if category["id"] == product["category_id"]
            ),
            None
        )

        product["category_name"] = (
            category["category"] if category else "No Category"
        )

    return products_response.data

