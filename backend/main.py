from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. Pydantic Schemas (As defined in Step 4 & 5) ---

class ItemCreate(BaseModel):
    """Schema for creating a new item (POST /items)."""
    name: str
    description: str | None = None
    price: float
    is_offer: bool | None = None

class ItemUpdate(BaseModel):
    """Schema for updating an existing item (PUT /items/{item_id})."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_offer: Optional[bool] = None

class ItemResponse(BaseModel):
    """Schema for item response (GET/PUT/POST)."""
    id: int
    name: str
    description: str | None = None
    price: float
    is_offer: bool | None = None

    class Config:
        # Required for Pydantic v2 compatibility if using ORM objects, good practice here.
        from_attributes = True

# --- 2. In-Memory Data Store Simulation ---

# Simulating a database using a dictionary
db: Dict[int, ItemResponse] = {}
next_id = 1

# --- 3. FastAPI Application Setup ---

app = FastAPI(
    title="Item Management API",
    description="Backend implementation following the specified plan.",
    version="1.0.0"
)

# --- 7. CORS Configuration ---
origins = [
    "http://localhost:3000",  # Example frontend URL
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- 4 & 5. API Endpoints Implementation ---

# Helper function for business logic validation (Step 6)
def validate_item_data(item_data: ItemCreate | ItemUpdate):
    if isinstance(item_data, ItemCreate) and item_data.price < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price cannot be negative."
        )
    # Note: Type validation (e.g., price being float) is handled automatically by Pydantic (422 error).

@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create an Item")
async def create_item(item: ItemCreate):
    """
    Create a new item in the database.
    """
    validate_item_data(item)
    
    global next_id
    new_id = next_id
    next_id += 1
    
    # Convert Pydantic model to dictionary and add ID
    item_dict = item.model_dump()
    response_item = ItemResponse(id=new_id, **item_dict)
    
    db[new_id] = response_item
    return response_item

@app.get("/items", response_model=List[ItemResponse], summary="List All Items")
async def read_items():
    """
    Retrieve a list of all items currently stored.
    """
    return list(db.values())

@app.get("/items/{item_id}", response_model=ItemResponse, summary="Get Item by ID")
async def read_item(item_id: int):
    """
    Retrieve a specific item using its unique ID.
    """
    # Step 6: Resource Not Found Handling (404)
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return db[item_id]

@app.put("/items/{item_id}", response_model=ItemResponse, summary="Update an Item")
async def update_item(item_id: int, item_update: ItemUpdate):
    """
    Update an existing item by ID. Only fields provided in the request body will be updated.
    """
    # Step 6: Resource Not Found Handling (404)
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    existing_item = db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    
    # Validate business logic for updates (specifically negative price)
    if 'price' in update_data and update_data['price'] is not None:
        new_price = update_data['price']
        if new_price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price cannot be negative."
            )

    # Apply updates safely
    updated_item = existing_item.copy(update=update_data)
    
    db[item_id] = updated_item
    return updated_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Item")
async def delete_item(item_id: int):
    """
    Delete an item permanently from the database.
    """
    # Step 6: Resource Not Found Handling (404)
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    del db[item_id]
    return