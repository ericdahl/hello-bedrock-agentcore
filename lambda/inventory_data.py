"""
Mock inventory database for Absurd Gadgets products.
Provides inventory lookup with fuzzy matching support.
"""

# Primary inventory database (keyed by SKU for fast lookup)
INVENTORY = {
    "ACM-006": {
        "sku": "ACM-006",
        "product_name": "Antigravity Coffee Mug",
        "in_stock": True,
        "quantity": 42,
        "restock_date": None
    },
    "IU-004": {
        "sku": "IU-004",
        "product_name": "Invisible Umbrella",
        "in_stock": False,
        "quantity": 0,
        "restock_date": "2024-02-01"
    },
    "QS-003": {
        "sku": "QS-003",
        "product_name": "Quantum Socks",
        "in_stock": True,
        "quantity": 156,
        "restock_date": None
    },
    "SPB-001": {
        "sku": "SPB-001",
        "product_name": "Self-Peeling Banana",
        "in_stock": True,
        "quantity": 89,
        "restock_date": None
    },
    "TRC-005": {
        "sku": "TRC-005",
        "product_name": "Telepathic Remote",
        "in_stock": True,
        "quantity": 23,
        "restock_date": None
    },
    "WTP-002": {
        "sku": "WTP-002",
        "product_name": "WiFi Toaster for Pets",
        "in_stock": False,
        "quantity": 0,
        "restock_date": "2024-01-25"
    }
}

# Product aliases for common search terms
PRODUCT_ALIASES = {
    "coffee mug": "ACM-006",
    "mug": "ACM-006",
    "antigravity mug": "ACM-006",
    "umbrella": "IU-004",
    "invisible umbrella": "IU-004",
    "socks": "QS-003",
    "quantum socks": "QS-003",
    "banana": "SPB-001",
    "self-peeling banana": "SPB-001",
    "remote": "TRC-005",
    "telepathic remote": "TRC-005",
    "toaster": "WTP-002",
    "pet toaster": "WTP-002",
    "wifi toaster": "WTP-002",
    "wifi toaster for pets": "WTP-002"
}


def find_product(identifier: str):
    """
    Find product by SKU or name with fuzzy matching.

    Args:
        identifier: Product name or SKU code

    Returns:
        dict: Inventory record or None if not found
    """
    if not identifier:
        return None

    identifier_lower = identifier.lower().strip()

    # Try exact SKU match first (case-insensitive)
    for sku, data in INVENTORY.items():
        if sku.lower() == identifier_lower:
            return data

    # Try alias match
    if identifier_lower in PRODUCT_ALIASES:
        sku = PRODUCT_ALIASES[identifier_lower]
        return INVENTORY.get(sku)

    # Try partial name match
    for sku, data in INVENTORY.items():
        product_name_lower = data["product_name"].lower()
        # Check if identifier is contained in product name or vice versa
        if identifier_lower in product_name_lower or product_name_lower in identifier_lower:
            return data

    return None


def get_inventory(product_identifier: str) -> dict:
    """
    Get inventory status for a product with formatted response.

    Args:
        product_identifier: Product name or SKU

    Returns:
        dict: Formatted inventory response with success status
    """
    product = find_product(product_identifier)

    if not product:
        return {
            "success": False,
            "message": f"Product '{product_identifier}' not found in our inventory. Please check the product name or SKU and try again."
        }

    # Build success response
    response = {
        "success": True,
        "product_name": product["product_name"],
        "sku": product["sku"],
        "in_stock": product["in_stock"],
        "quantity_available": product["quantity"]
    }

    # Add helpful message
    if product["in_stock"]:
        response["message"] = f"We have {product['quantity']} units of {product['product_name']} (SKU: {product['sku']}) in stock."
    else:
        if product["restock_date"]:
            response["message"] = f"{product['product_name']} (SKU: {product['sku']}) is currently out of stock. Expected restock date: {product['restock_date']}."
        else:
            response["message"] = f"{product['product_name']} (SKU: {product['sku']}) is currently out of stock. Please check back later."

    return response
