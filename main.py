from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- 1. Schema Definitions (Pydantic Models) חלק

# Note: Using Python 3.10+ union syntax ( | ) as shown in the plan examples.

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the item")
    description: str | None = Field(None, description="Optional description")
    price: float = Field(..., gt=0, description="Price must be greater than zero")

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)

class ItemInDB(ItemCreate):
    id: int = Field(..., description="Unique identifier for the item")
    is_active: bool = True

# --- 2. Initialization and Setup חלק

app = FastAPI(
    title="Item Management API",
    version="1.0.0"
)

# CORS Configuration (as per plan)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. In-Memory Database Simulation חלק

# db structure: {item_id: ItemInDB_dict}
db: Dict[int, Dict[str, Any]] = {}
next_id: int = 1

# --- 4. Endpoint Implementations חלק

# Endpoint 1: POST /items/ - Creates a new item.
@app.post("/items/", response_model=ItemInDB, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global next_id
    
    # Convert Pydantic model to dictionary for storage simulation
    # Using model_dump() for Pydantic V2 compatibility
    new_item_data = item.model_dump()
    new_item_data['id'] = next_id
    new_item_data['is_active'] = True
    
    db[next_id] = new_item_data
    next_id += 1
    
    return new_item_data

# Endpoint 2: GET /items/ - Retrieves all items.
@app.get("/items/", response_model=List[ItemInDB])
async def read_all_items():
    return list(db.values())

# Endpoint 3: GET /items/{item_id} - Retrieves a specific item by ID.
@app.get("/items/{item_id}", response_model=ItemInDB)
async def read_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found")
    
    return db[item_id]

# Endpoint 4: PUT /items/{item_id} - Updates an existing item (implements partial update logic).
@app.put("/items/{item_id}", response_model=ItemInDB)
async def update_item(item_id: int, item_update: ItemUpdate):
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found")
    
    existing_item = db[item_id]
    # Use model_dump(exclude_unset=True) to only get fields that were explicitly provided in the request body
    update_data = item_update.model_dump(exclude_unset=True)
    
    # Apply updates
    for key, value in update_data.items():
        # If a field like 'price' was explicitly sent as null in JSON, value will be None.
        # We only update if the value is not None (i.e., it's a valid update value or an explicit 0.0, which Pydantic already validated).
        if value is not None:
            existing_item[key] = value
            
    db[item_id] = existing_item
    return existing_item

# Endpoint 5: DELETE /items/{item_id} - Deletes an item.
@app.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with ID {item_id} not found")

    del db[item_id]
    
    # Returning the specific message structure requested in the plan for DELETE success
    return {"message": "Item deleted"}