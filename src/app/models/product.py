from sqlmodel import Field, SQLModel
from enum import Enum
from pydantic import field_validator
import re



class CategoriesEnum(str, Enum):
    FRUITS      = "Fruits"
    ELECTRONICS = "Electronics"
    Clothes     = "Clothes"

class ProductBase(SQLModel):
    name     : str             = Field(min_length=3, max_length=80, unique=True)
    price    : float           = Field(gt = 0)
    quantity : int             = Field(gt = 0)
    category : CategoriesEnum
    sku      : str             = Field(regex=r"^[A-Z]{3}-\d{4}$", unique= True)
    
    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        pattern = r"^[A-Z]{3}-\d{4}$"
        
        if not re.match(pattern, value):
            raise ValueError(
                "The Sku must be like ABC-123"
            )
        return value
    
    
class ProductCreate(ProductBase):
    pass

#Updated Product 
class UpdateProduct(SQLModel):
    name     : str            | None = Field(default = None, min_length=3, max_length=80)
    price    : float          | None = Field(default = None, gt = 0)
    quantity : int            | None = Field(default = None, gt = 0)
    category : CategoriesEnum | None = None
    sku      : str            | None = Field(default=None, regex=r"^[A-Z]{3}-\d{4}$")
    
    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        pattern = r"^[A-Z]{3}-\d{4}$"
        
        if not re.match(pattern, value):
            raise ValueError(
                "The Sku must be like ABC-123"
            )
        return value
    
#Database Model
class Product(ProductBase, table=True):
    __tablename__ = "app_inv_products"
    
    id : int | None = Field(default=None, primary_key=True)
    