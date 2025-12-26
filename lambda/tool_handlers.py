"""
Tool execution handlers for Bedrock function calling.
Dispatches and executes tool requests from the model.
"""

from inventory_data import get_inventory


def handle_check_inventory(product_identifier: str) -> dict:
    """
    Handle inventory check tool execution.

    Args:
        product_identifier: Product name or SKU to check

    Returns:
        dict: Inventory status with success flag and details
    """
    try:
        print(f"[Tool] Checking inventory for: {product_identifier}")
        result = get_inventory(product_identifier)
        print(f"[Tool] Inventory result: {result}")
        return result
    except Exception as e:
        print(f"[Tool] Error checking inventory: {str(e)}")
        return {
            "success": False,
            "message": f"An error occurred while checking inventory: {str(e)}"
        }


def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool by name with provided input.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Input parameters for the tool

    Returns:
        dict: Tool execution result

    Raises:
        ValueError: If tool name is not recognized
    """
    print(f"[Tool] Executing tool: {tool_name} with input: {tool_input}")

    if tool_name == "check_inventory":
        product_identifier = tool_input.get("product_identifier", "")
        return handle_check_inventory(product_identifier)
    else:
        error_msg = f"Unknown tool: {tool_name}"
        print(f"[Tool] Error: {error_msg}")
        return {
            "success": False,
            "message": error_msg
        }
