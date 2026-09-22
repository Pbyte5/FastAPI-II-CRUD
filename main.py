from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, create_engine,Session, select
from contextlib import asynccontextmanager


#Connetion with Supabase
DATABASE_URL = "postgresql://postgres.ewewniiixfunicnwsbyr:RiwiMaku57a#@aws-0-us-east-2.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


#Template Model
class ProductBase(SQLModel):
    name     : str
    price    : float
    quantity : int
    category : str 

#Create Product Model
class ProductCreate(ProductBase):
    pass

class UpdateProduct(ProductBase):
    pass
    
#Database Model
class Product(ProductBase, table=True):
     id : int | None = Field(default=None, primary_key=True)
    

@asynccontextmanager
async def life_span(app:FastAPI):
    init_db()
    yield

app = FastAPI(
    title="API Inventory",
    lifespan=life_span
)

@app.get("/products/",response_model=list[Product])
async def get_all_products(db:Session = Depends(get_session)):
    products = db.exec(select(Product)).all()
    return products


@app.post("/products/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def new_product(new_product: ProductCreate, db:Session = Depends(get_session)):
    try:
        db_product = Product.model_validate(new_product)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error, invalid values: {str(err)}"
        )

@app.delete("/products/{id}")
async def deleted_product(id:int, db:Session= Depends(get_session)):
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
@app.patch("/products/{id}")
async def update_product(id:int, db:Session=Depends(get_session)):
    product = db.get(Product, id)
    
    if not product: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update: Product not found!"
        )

        




if __name__ == "__main__":
    print("You are in main")
