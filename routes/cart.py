from fastapi import APIRouter
from pydantic import BaseModel
from supabase_client import supabase

router = APIRouter()

class CartItem(BaseModel):
    user_id: int
    product_id: int
    product_name: str
    price: float
    image: str | None = None
    cart_quantity: int = 1

#Add cart into supabase
# @router.post("/cart")
# def add_to_cart(
#     user_id: str,
#     product_id: int,
#     product_name: str,
#     price: float,
#     image: str,
#     cart_quantity: int = 1
# ):
#     existing = (
#         supabase
#         .table("cart_items")
#         .select("*")
#         .eq("user_id", user_id)
#         .eq("product_id", product_id)
#         .execute()
#     )
#     if existing.data:
#         old_quantity = existing.data[0]["cart_quantity"]

#         new_quantity = old_quantity + cart_quantity

#         response = (
#             supabase
#             .table("cart_items")
#             .update({
#                 "cart_quantity": new_quantity
#             })
#             .eq("id", existing.data[0]["id"])
#             .execute()
#         )

#     else:
#         response = (
#             supabase
#             .table("cart_items")
#             .insert({
#                 "user_id": user_id,
#                 "product_id": product_id,
#                 "product_name": product_name,
#                 "price": price,
#                 "image": image,
#                 "cart_quantity": cart_quantity
#             })
#             .execute()
#         )

#     return {
#         "message": "Product added to cart",
#         "cart": response.data
#     }

# @router.post("/cart")
# def add_to_cart(item: CartItem):

#     existing = (
#         supabase
#         .table("cart_items")
#         .select("*")
#         .eq("user_id", item.user_id)
#         .eq("product_id", item.product_id)
#         .execute()
#     )

#     if existing.data:

#         old_quantity = existing.data[0]["cart_quantity"]

#         new_quantity = old_quantity + item.cart_quantity

#         response = (
#             supabase
#             .table("cart_items")
#             .update({
#                 "cart_quantity": new_quantity
#             })
#             .eq("id", existing.data[0]["id"])
#             .execute()
#         )

#     else:

#         response = (
#             supabase
#             .table("cart_items")
#             .insert({
#                 "user_id": item.user_id,
#                 "product_id": item.product_id,
#                 "product_name": item.product_name,
#                 "price": item.price,
#                 "image": item.image,
#                 "cart_quantity": item.cart_quantity
#             })
#             .execute()
#         )

#     return {
#         "message": "Product added to cart",
#         "cart": response.data
#     }

@router.post("/cart")
def add_to_cart(item: CartItem):

    existing = (
        supabase
        .table("cart_items")
        .select("*")
        .eq("user_id", item.user_id)
        .eq("product_id", item.product_id)
        .execute()
    )

    if existing.data:

        old_quantity = existing.data[0]["cart_quantity"]

        new_quantity = (
            old_quantity + item.cart_quantity
        )

        response = (
            supabase
            .table("cart_items")
            .update({
                "cart_quantity": new_quantity
            })
            .eq("id", existing.data[0]["id"])
            .execute()
        )

    else:

        response = (
            supabase
            .table("cart_items")
            .insert({
                "user_id": item.user_id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "price": item.price,
                "image": item.image,
                "cart_quantity": item.cart_quantity
            })
            .execute()
        )


    # Update product stock

    stock_response = (
        supabase
        .table("products")
        .select("quantity")
        .eq("id", item.product_id)
        .single()
        .execute()
    )

    product = stock_response.data

    if not product:
        return {
            "message": "Product not found"
        }

    current_quantity = product["quantity"]

    new_quantity = (
        current_quantity - item.cart_quantity
    )

    if new_quantity < 0:
        return {
            "message": "Not enough stock"
        }

    supabase \
        .table("products") \
        .update({
            "quantity": new_quantity
        }) \
        .eq("id", item.product_id) \
        .execute()


    return {
        "message": "Product added to cart",
        "cart": response.data
    }

#GET CART ITEM
@router.get("/cart/{user_id}")
def get_cart(user_id: str):

    response = (
        supabase
        .table("cart_items")
        .select("*")
        .eq("user_id", user_id)
        .order("id")
        .execute()
    )

    return response.data

#DELETE CART ITEM
# @router.delete("/cart/{cart_id}")
# def delete_cart_item(cart_id: int):

#     response = (
#         supabase
#         .table("cart_items")
#         .delete()
#         .eq("id", cart_id)
#         .execute()
#     )

#     return {
#         "message": "Cart item deleted"
#     }

@router.delete("/cart/{cart_id}")
def delete_cart_item(cart_id: int):

    # 1. Pehle cart item find karo
    cart_response = (
        supabase
        .table("cart_items")
        .select("*")
        .eq("id", cart_id)
        .single()
        .execute()
    )

    cart_item = cart_response.data

    if not cart_item:
        return {
            "message": "Cart item not found"
        }

    # 2. Cart item ki information lo
    product_id = cart_item["product_id"]
    cart_quantity = cart_item["cart_quantity"]

    # 3. Product ka current stock lo
    product_response = (
        supabase
        .table("products")
        .select("quantity")
        .eq("id", product_id)
        .single()
        .execute()
    )

    product = product_response.data

    if not product:
        return {
            "message": "Product not found"
        }

    # 4. Cart quantity stock mein wapas add karo
    current_stock = product["quantity"]

    new_stock = current_stock + cart_quantity

    stock_response = (
        supabase
        .table("products")
        .update({
            "quantity": new_stock
        })
        .eq("id", product_id)
        .execute()
    )

    # 5. Cart item delete karo
    delete_response = (
        supabase
        .table("cart_items")
        .delete()
        .eq("id", cart_id)
        .execute()
    )

    return {
        "message": "Cart item deleted and stock restored",
        "product_id": product_id,
        "restored_quantity": cart_quantity,
        "new_stock": new_stock
    }

#CHANGE CART QUANTITY
@router.patch("/cart/{cart_id}")
def update_cart_quantity(cart_id: int , cart_quantity: int):
    if cart_quantity < 1 :
        return{
            "message": "Quantity cannot be less than 1"
        }
    response = (
        supabase
        .table("cart_items")
        .update(
            {"cart_quantity": cart_quantity}
            )
        .eq("id", cart_id)
        .execute()
    )
    return{
        "message": "Quantity be updated",
        "cart": response.data
    }


#Update product quantity
# @router.patch("/products/{product_id}/stock")
# def update_product_stock(product_id: int, quantity_change: int):

#     response = (
#         supabase
#         .table("products")
#         .select("quantity")
#         .eq("id", product_id)
#         .single()
#         .execute()
#     )

#     product = response.data

#     if not product:
#         return {
#             "message": "Product not found"
#         }

#     current_quantity = product["quantity"]

#     new_quantity = current_quantity + quantity_change

#     if new_quantity < 0:
#         return {
#             "message": "Not enough stock"
#         }

#     update_response = (
#         supabase
#         .table("products")
#         .update({
#             "quantity": new_quantity
#         })
#         .eq("id", product_id)
#         .execute()
#     )

#     return {
#         "message": "Stock updated successfully",
#         "product_id": product_id,
#         "quantity": new_quantity
#     }

