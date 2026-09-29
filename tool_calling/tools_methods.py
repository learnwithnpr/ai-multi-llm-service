from typing import Optional
from products_list import list_of_products, list_of_inventories, list_of_discounts


def search_products_by_name(name:Optional[str]= None):
    results =[]
    
    for product in list_of_products:
        if name:
            if name in product["name"]:                
                results.append(product)
            else :
                results.append(list_of_products)
                continue
    return {
        "success":True,
        "count":len(results),
        "products":results
    }

def check_invertory_details(name:str):
    results =[]
    product_id = None
    for product in list_of_products:
        if product["name"] == name:
            product_id = product["id"]
            results.append({"success":True,"product":product["name"],
                "invertory":list_of_inventories[product_id]})
    
    if not results:
        return {"success":False, "error": "Product not found"}

    return results


def calculate_discount(name: str, quantity: int, discount_code: str = "NO_DISCOUNT"):
    """Calculates the final price after applying a discount code."""
    product = None
    for item in list_of_products:
        if item["name"] == name or item["id"] == name:
            product = item
            break

    if product is None:
        return {"success": False, "error": "Product not found"}

    if quantity <= 0:
        return {"success": False, "error": "Quantity must be greater than zero"}

    if discount_code not in list_of_discounts:
        return {
            "success": False,
            "error": f"Invalid discount code. Available: {list(list_of_discounts.keys())}"
        }

    unit_price = product["price"]
    subtotal = unit_price * quantity
    discount_percentage = list_of_discounts[discount_code]
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