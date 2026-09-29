from tools_methods import search_products_by_name, check_invertory_details, calculate_discount


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
},

{
    "type":"function",
    "name":"calculate_discount",
    "description":"Calculate the final price of a product after applying quantity and a discount code (WELCOME10, SAVE20, NO_DISCOUNT)",
    "parameters":{
        "type":"object",
        "properties":{
            "name":{"type":"string", "description":"Product name or product ID"},
            "quantity":{"type":"integer", "description":"Number of units to buy"},
            "discount_code":{"type":"string", "description":"Discount code such as WELCOME10, SAVE20, or NO_DISCOUNT"}
        },
        "required":["name", "quantity", "discount_code"]
    }
}
]

tools_available = {
                    "search_products_by_name":search_products_by_name,
                    "check_invertory_details":check_invertory_details,
                    "calculate_discount":calculate_discount
                    }