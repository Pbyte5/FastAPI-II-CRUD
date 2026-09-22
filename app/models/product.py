from sqlmodel import Field, SQLModel
from enum import Enum

class CategoriesEnum(str, Enum):
    FRUITS      = "Fruits"
    ELECTRONICS = "Electronics"
    Clothes     = "Clothes"

class ProductBase(SQLModel):
    name     : str   = Field(min_length=3, max_length=80)
    price    : float = Field(gt = 0)
    quantity : int   = Field(gt = 0)
    category : CategoriesEnum
    sku      : str = Field(regex=r"^[A-Z]{3}-\d{4}$")
    
class ProductCreate(ProductBase):
    pass

#Updated Product 
class UpdateProduct(SQLModel):
    name     : str            | None = Field(default = None, min_length=3, max_length=80)
    price    : float          | None = Field(default = None, gt = 0)
    quantity : int            | None = Field(default = None, gt = 0)
    category : CategoriesEnum | None = None
    sku      : str            | None = Field(default=None, regex=r"^[A-Z]{3}-\d{4}$")
    pass
    
#Database Model
class Product(ProductBase, table=True):
     id : int | None = Field(default=None, primary_key=True)
    