from mcp.server.mcpserver import MCPServer
from tools_methods import search_products_by_name
from products_list import list_of_inventories

mcp = MCPServer("ecommerce-agent")


@mcp.tool()
def search_products_by_name(name:str):
    result = {
        "success":True,
        "products":search_products_by_name(name)
    }
    return result

@mcp.tool()
def check_invertory_details(name:str):
    results = {
        "success":True,
        "product":name,
        "invertory":list_of_inventories.get(name, "Product not found")
    }
    return results