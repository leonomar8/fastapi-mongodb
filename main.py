from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# Modelo de datos
class Item(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None

# Conexión a MongoDB
client = MongoClient("mongodb://ec2-3-80-218-210.compute-1.amazonaws.com:27017/")
db = client["my_database"]

# Create - Crear un nuevo ítem
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    inserted_item = db.items.insert_one(item.dict())
    item.id = str(inserted_item.inserted_id)
    return item

# Read - Obtener un ítem por ID
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str):
    item = db.items.find_one({"_id": ObjectId(item_id)})
    if item:
        return Item(**item)
    raise HTTPException(status_code=404, detail="Item not found")

# Read all - Obtener todos los ítems
@app.get("/items/", response_model=List[Item])
def read_items():
    items = db.items.find()
    return [Item(**item) for item in items]

# Update - Actualizar un ítem por ID
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, updated_item: Item):
    updated_item_data = updated_item.dict(exclude_unset=True)
    db.items.update_one({"_id": ObjectId(item_id)}, {"$set": updated_item_data})
    return updated_item

# Delete - Eliminar un ítem por ID
@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    result = db.items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)