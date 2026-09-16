import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# 1. Mock E-commerce Data
products = [
    {"id": "P101", "name": "Nike Air Max 270", "category": "shoes", "brand": "Nike", "price": 4999, "rating": 4.5},
    {"id": "P102", "name": "Adidas Ultraboost", "category": "shoes", "brand": "Adidas", "price": 6499, "rating": 4.6},
    {"id": "P103", "name": "Apple AirPods Pro", "category": "electronics", "brand": "Apple", "price": 19999, "rating": 4.7},
    {"id": "P104", "name": "Sony WH-1000XM5", "category": "electronics", "brand": "Sony", "price": 24999, "rating": 4.8},
    {"id": "P105", "name": "Levi's 511 Jeans", "category": "clothing", "brand": "Levi's", "price": 2999, "rating": 4.4}
]

inventory = {
    "P101": {"Hyderabad": 12, "Bangalore": 5, "Mumbai": 8},
    "P102": {"Hyderabad": 0, "Bangalore": 8, "Mumbai": 3},
    "P103": {"Hyderabad": 20, "Bangalore": 10, "Mumbai": 15},
    "P104": {"Hyderabad": 4, "Bangalore": 0, "Mumbai": 6},
    "P105": {"Hyderabad": 15, "Bangalore": 7, "Mumbai": 10}
}

discounts = {
    "WELCOME10": 10,
    "SAVE20": 20,
    "NO_DISCOUNT": 0
}


# 2. Tool Implementations
def search_products(query: str, max_price: float | None = None):
    """Search products based on a text query."""
    results = []
    query = query.lower()

    for product in products:
        searchable_text = (product["name"] + " " + product["brand"] + " " + product["category"]).lower()
        if query in searchable_text:
            if max_price is not None:
                if product["price"] > max_price:
                    continue
            results.append(product)

    return {
        "success": True,
        "count": len(results),
        "products": results
    }

def get_product_details(product_id: str):
    """Returns detailed information for a product."""
    for product in products:
        if product["id"] == product_id:
            return {"success": True, "product": product}
    return {"success": False, "error": f"Product {product_id} not found"}

def check_inventory(product_id: str, city: str):
    """Checks whether a product is available in a specific city."""
    if product_id not in inventory:
        return {"success": False, "error": "Product not found in inventory"}
    
    city_inventory = inventory[product_id]
    quantity = city_inventory.get(city, 0)
    
    return {
        "success": True,
        "product_id": product_id,
        "city": city,
        "available_quantity": quantity,
        "in_stock": quantity > 0
    }

def calculate_final_price(product_id: str, quantity: int, discount_code: str = "NO_DISCOUNT"):
    """Calculates total price after applying discount."""
    product = None
    for item in products:
        if item["id"] == product_id:
            product = item
            break

    if product is None:
        return {"success": False, "error": "Product not found"}
    
    if quantity <= 0:
        return {"success": False, "error": "Quantity must be greater than zero"}
    
    if discount_code not in discounts:
        return {"success": False, "error": "Invalid discount code"}

    unit_price = product["price"]
    subtotal = unit_price * quantity
    discount_percentage = discounts[discount_code]
    discount_amount = subtotal * discount_percentage / 100
    final_price = subtotal - discount_amount

    return {
        "success": True,
        "product": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": subtotal,
        "discount_code": discount_code,
        "discount_percentage": discount_percentage,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "currency": "INR"
    }


# 3. Tool Schemas
tools = [
    {
        "type": "function",
        "name": "search_products",
        "description": (
            "Search for products in the e-commerce catalog "
            "based on keywords and optionally filter by maximum price."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name, category, or brand to search for."
                },
                "max_price": {
                    "type": ["number", "null"],
                    "description": "Maximum acceptable price in INR."
                }
            },
            "required": ["query", "max_price"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_product_details",
        "description": "Returns detailed information about a product using its product ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Unique product ID."
                }
            },
            "required": ["product_id"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "check_inventory",
        "description": "Checks whether a product is available in a particular city.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string"
                },
                "city": {
                    "type": "string"
                }
            },
            "required": ["product_id", "city"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "calculate_final_price",
        "description": "Calculates the final price of a product after quantity and discount are applied.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string"
                },
                "quantity": {
                    "type": "integer"
                },
                "discount_code": {
                    "type": "string"
                }
            },
            "required": ["product_id", "quantity", "discount_code"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# 4. Tool Registry
available_tools = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "check_inventory": check_inventory,
    "calculate_final_price": calculate_final_price
}

# 5. Example Execution Loop (similar to tool_calling.py)
if __name__ == "__main__":
    print("Testing Shopping Agent...")
    
    # Try calling the model
    try:
        response = client.responses.create(
            model='gpt-4o-mini', 
            input="If I buy two Nike Air Max using WELCOME10, how much will I pay?", 
            tools=tools
        )
        
        print("\nModel Response:")
        print(response)
        
        for item in response.output:
            if item.type == "function_call":
                tool = available_tools[item.name]
                arguments = json.loads(item.arguments)
                print(f"\nExecuting tool: {item.name}")
                print(f"Arguments: {arguments}")
                
                result = tool(**arguments)
                print(f"Result: {json.dumps(result, indent=2)}")
                
                # Feedback the tool output back into the conversation
                response = client.responses.create(
                    model="gpt-4o-mini", 
                    input=[{
                        "type": "function_call_output", 
                        "call_id": item.call_id, 
                        "output": json.dumps(result)
                    }], 
                    previous_response_id=response.id
                )
                print("\nFollow-up Model Response:")
                print(response.output)
                
    except Exception as e:
        print(f"Error during execution: {e}")
