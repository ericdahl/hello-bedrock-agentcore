"""Custom tool for checking inventory."""
from strands import tool
from typing import Dict
import sys
import os

# Add parent directory to path to import inventory_data
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inventory_data import get_inventory


@tool
def check_inventory(product_identifier: str) -> Dict:
    """Check real-time inventory status for Absurd Gadgets products.

    Use this tool when customers ask about product availability, stock status,
    quantity available, or whether items are in stock. Returns current stock
    levels and availability information.

    Args:
        product_identifier: The product name or SKU code to check. Can be a
            full product name (e.g., 'Antigravity Coffee Mug'), partial name
            (e.g., 'coffee mug'), or SKU code (e.g., 'ACM-006').

    Returns:
        dict: Inventory status with keys:
            - success (bool): Whether the lookup was successful
            - product_name (str): Full product name
            - sku (str): Product SKU code
            - in_stock (bool): Whether product is available
            - quantity_available (int): Number of units in stock
            - message (str): Human-readable status message
    """
    return get_inventory(product_identifier)
