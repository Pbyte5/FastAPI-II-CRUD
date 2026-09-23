from fastapi import FastAPI, HTTPException, status
from sqlmodel import  select
from src.app.models import Product, ProductCreate, UpdateProduct
from src.shared.database.session import life_span, SessionDep
from sqlalchemy.exc import IntegrityError

app = FastAPI(
    title="API Inventory",
    lifespan=life_span
)
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
            detail= f"Error, there is a conflict between products names or sku"
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
