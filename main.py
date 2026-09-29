from fastapi import FastAPI, HTTPException, status, UploadFile, File
from sqlmodel import  select
from src.app.models import Product, ProductCreate, UpdateProduct
from src.shared.database.session import life_span, SessionDep
from sqlalchemy.exc import IntegrityError
import boto3
import os
import uuid

app = FastAPI(
    title="API Inventory",
    lifespan=life_span
)
s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
S3_BUCKET = os.environ.get("S3_BUCKET")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@app.get("/health")
def health():
    return {"status": "ok"}

# --- AWS: POST /images (sube la imagen a S3 con Boto3) ---
@app.post("/images")
async def upload_image(file: UploadFile = File(...)):

    if not S3_BUCKET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3_BUCKET is not configured"
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed"
        )

    filename = os.path.basename(file.filename or "image")
    key = f"images/{uuid.uuid4()}-{filename}"

    try:
        s3.upload_fileobj(
            file.file,
            S3_BUCKET,
            key,
            ExtraArgs={"ContentType": file.content_type}
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading to S3: {str(err)}"
        )

    return {
        "message": "Image uploaded successfully",
        "bucket": S3_BUCKET,
        "key": key
    }


## ONLY GETS ONE PRODUCT
@app.get(
    "/products/",
    response_model=list[Product], 
    status_code=status.HTTP_200_OK
    )

async def get_all_products(db:SessionDep):
    
    products = (
        db.
        exec(select(Product)).
        all())
    
    return products

## ONLY POST ONE PRODUCT
@app.post(
    "/products/", 
    response_model=Product, 
    status_code=status.
    HTTP_201_CREATED
    )

async def new_product(new_product: ProductCreate, db: SessionDep):
    
    try:
        
        db_product = Product.model_validate(new_product)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return db_product
    
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail= f"Error, The names or sku already exits! "
        ) 
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error, invalid values: {str(err)}"
        )

            
#DELETE ONE PRODUCT
@app.delete("/products/{id}")
async def deleted_product(id:int, db:SessionDep):
    
    product = db.get(Product, id)
    
    if not product:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Remove: Product not found!")
    
    try: 
        db.delete(product)
        db.commit()
        return {"message" :f"Product with  {id} deleted: Todo makia!"}
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Error, product not removed {str(err)}"
        )
        
        
#UPDATED PRODUCT
@app.patch("/products/{id}")
async def update_product(id:int,product_data:UpdateProduct, db:SessionDep):
    
    db_product = db.get(Product, id)
    
    if not db_product: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update: Product not found!"
        )
    
    updated_data = product_data.model_dump(exclude_unset=True)
    db_product.sqlmodel_update(updated_data)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product



if __name__ == "__main__":
    print("You are in main")
