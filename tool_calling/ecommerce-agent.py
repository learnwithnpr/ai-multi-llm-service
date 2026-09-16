from enum import auto
from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import Optional

load_dotenv()

client= OpenAI()

list_of_products = [
    {"id": "P101", "name": "Nike Air Max 270", "category": "shoes", "brand": "Nike", "price": 4999, "rating": 4.5,},
    {"id": "P102", "name": "Adidas Ultraboost", "category": "shoes", "brand": "Adidas", "price": 6499, "rating": 4.6},
    {"id": "P103", "name": "Apple AirPods Pro", "category": "electronics", "brand": "Apple", "price": 19999, "rating": 4.7},
    {"id": "P104", "name": "Sony WH-1000XM5", "category": "electronics", "brand": "Sony", "price": 24999, "rating": 4.8},
    {"id": "P105", "name": "Levi's 511 Jeans", "category": "clothing", "brand": "Levi's", "price": 2999, "rating": 4.4}
]

list_of_inventories = {
    "P101": {"Hyderabad": 12, "Bangalore": 5, "Mumbai": 8},
    "P102": {"Hyderabad": 0, "Bangalore": 8, "Mumbai": 3},
    "P103": {"Hyderabad": 20, "Bangalore": 10, "Mumbai": 15},
    "P104": {"Hyderabad": 4, "Bangalore": 0, "Mumbai": 6},
    "P105": {"Hyderabad": 15, "Bangalore": 7, "Mumbai": 10}
}

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

tools_available = {
                    "search_products_by_name":search_products_by_name,
                    "check_invertory_details":check_invertory_details
                    }



tools = [{
    "type":"function",
    "name":"search_products_by_name",
    "description":"Search for products by name and if it is not given get the entire list",
    "parameters":{"type":"object", "properties":{"name":{"type":"string"}}, "required":["name"]}
},

{
    "type":"function",
    "name":"check_invertory_details",
    "description":"Check inventory details like price and quantity available in different cities like bangalore, hyderabad, mumbai of the product using product name",
    "parameters":{"type":"object", "properties":{"name":{"type":"string"}}, "required":["name"]}
}]

response = client.responses.create(model='gpt-4o-mini', input= "what is the price of Apple AirPods Pro and how many are available in Hyderabad?", tools=tools, tool_choice="auto")

max_steps = 5
step = 0

print("-----------------Response 1st----------------")
print(response)
print("-----------------Response 1st----------------")

print("-----------------Response output----------------")
print(response.output)
print("-----------------Response output----------------")


while step < max_steps:
    step += 1
    print("step :",step)

    has_tool_call = False
    tools_output = []

    for item in response.output:
        if item.type == "function_call":
            has_tool_call = True
            tool = tools_available[item.name]
            arguments = json.loads(item.arguments)
            result = tool(**arguments)
            tools_output.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result)
        })

        elif item.type == "message":
            for text_chunk in item.content:
                print(f"\n Agent: {text_chunk.text}")
    print("-----------------tools output----------------")
    print(tools_output)
    print("-----------------tools output----------------")
    
    if not has_tool_call:
        break

    response = client.responses.create(
        model="gpt-4o-mini",
        input=tools_output,
        previous_response_id=response.id
    )


