from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

products = [
    {
       "id": 1, 
       "name": "Wireless Mouse", 
       "price": 499,
       "category": "Electronics",
       "in_stock": True 
    },
    {
       "id": 2, 
       "name": "Notebook", 
       "price": 99,
       "category": "Stationery",
       "in_stock": True 
    },
    {
        "id": 3, 
        "name": "USB Hub", 
        "price": 799, 
        "category": "Electronics",
        "in_stock": False
    },
    {
       "id": 4, 
       "name": "Pen set", 
       "price": 49, 
       "category": "Stationery",
        "in_stock": True 
    },
    {
       "id": 5, 
       "name": "Laptop Stand", 
       "price": 1299, 
       "category": "Electronics",
       "in_stock": True 
    },
    {
       "id": 6, 
       "name": "Mechanical Keyboard", 
       "price": 2499,
       "category": "Electronics",
       "in_stock": True 
    },
    {
        "id": 7, 
        "name": "Webcam",
        "price": 1899, 
        "category": "Electronics", 
        "in_stock": False
    },
]
feedback = []
orders = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: list[OrderItem]

class OrderRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)

@app.get("/")
def home():
    return {"message": "Hello Pradnya, FastAPI working!"}

@app.get("/about")
def about():
    return {"message": "This is my first FastAPI project"}

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered_products = []

    for product in products:
        if product["category"].lower() == category_name.lower():
            filtered_products.append(product)

    if len(filtered_products) == 0:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products
    }

@app.get("/products/instock")
def get_instock_products():

    instock_products = []

    for product in products:
        if product["in_stock"] == True:
            instock_products.append(product)

    return {
        "in_stock_products": instock_products,
        "count": len(instock_products)
    }

@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = 0
    out_of_stock = 0
    categories = []

    for product in products:

        if product["in_stock"]:
            in_stock += 1
        else:
            out_of_stock += 1

        if product["category"] not in categories:
            categories.append(product["category"])

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            matched_products.append(product)

    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "total_matches": len(matched_products)
    }

@app.get("/products/deals")
def product_deals():

    cheapest = products[0]
    expensive = products[0]

    for product in products:

        if product["price"] < cheapest["price"]:
            cheapest = product

        if product["price"] > expensive["price"]:
            expensive = product

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

@app.get("/products/filter")
def filter_products(min_price: int = None, max_price: int = None, category: str = None):

    result = products

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if category is not None:
        result = [p for p in result if p["category"] == category]

    return result

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }

@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = 0
    out_of_stock_count = 0

    cheapest = products[0]
    most_expensive = products[0]

    categories = []

    for product in products:

        if product["in_stock"]:
            in_stock_count += 1
        else:
            out_of_stock_count += 1

        if product["price"] < cheapest["price"]:
            cheapest = product

        if product["price"] > most_expensive["price"]:
            most_expensive = product

        if product["category"] not in categories:
            categories.append(product["category"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product_found = None

        for product in products:
            if product["id"] == item.product_id:
                product_found = product
                break

        if product_found is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if product_found["in_stock"] == False:
            failed.append({
                "product_id": item.product_id,
                "reason": f'{product_found["name"]} is out of stock'
            })
            continue

        subtotal = product_found["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product_found["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

@app.post("/orders")
def create_order(order: OrderRequest):

    order_data = {
        "id": len(orders) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(order_data)

    return {
        "message": "Order placed successfully",
        "order": order_data
    }

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}

