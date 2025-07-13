```python
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Production Ready API", version="1.0.0")


# Define request and response models
class ItemRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    quantity: int
    total: float


# In-memory database simulation
fake_db = {}
item_id_counter = 1


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


# Create item endpoint
@app.post("/items", response_model=ItemResponse, tags=["Items"])
async def create_item(item: ItemRequest):
    global item_id_counter
    item_id = item_id_counter
    item_id_counter += 1

    total = item.price * item.quantity
    item_data = {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "quantity": item.quantity,
        "total": total,
    }

    fake_db[item_id] = item_data
    logger.info(f"Item created: {item_data}")
    return item_data


# Get item by ID endpoint
@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def get_item(item_id: int):
    item = fake_db.get(item_id)
    if not item:
        logger.warning(f"Item not found: {item_id}")
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
```