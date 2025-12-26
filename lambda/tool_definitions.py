"""
Bedrock tool definitions for the Absurd Gadgets chatbot.
Defines tool schemas following AWS Bedrock converse API specification.
"""

# Inventory check tool definition
INVENTORY_CHECK_TOOL = {
    "toolSpec": {
        "name": "check_inventory",
        "description": "Checks real-time inventory status for Absurd Gadgets products. Use this tool when customers ask about product availability, stock status, quantity available, or whether items are in stock. Returns current stock levels and availability information.",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "product_identifier": {
                        "type": "string",
                        "description": "The product name or SKU code to check. Can be a full product name (e.g., 'Antigravity Coffee Mug'), partial name (e.g., 'coffee mug'), or SKU code (e.g., 'ACM-006')."
                    }
                },
                "required": ["product_identifier"]
            }
        }
    }
}

# Tool configuration for Bedrock converse API
TOOL_CONFIG = {
    "tools": [INVENTORY_CHECK_TOOL]
}
