from fastapi import APIRouter
from supabase_client import supabase
from fastapi import Form, File, UploadFile
import uuid

router = APIRouter()

#add product to supabase
@router.post("/products")
async def add_product( 
    name: str = Form(...),   #Form(...) is used because your product request is sending both normal text/number data AND an image file.
    description: str = Form(...),
    category_id: int = Form(...),
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
            "category_id": category_id,
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


@router.get("/categories")
def get_categories():

    response = (
        supabase
        .table("categories")
        .select("*")
        .order("id")
        .execute()
    )

    return response.data

