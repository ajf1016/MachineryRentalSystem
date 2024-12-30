from modules.database import fetch_all_products, update_product
import datetime


def detect_rfid(tag_id):
    """
    Detect RFID tag and determine the flow (rented or returned).
    """
    products = fetch_all_products()
    product = next((p for p in products if p[2] == tag_id), None)

    if not product:
        return {"error": "Product not found"}

    product_id, name, tag_id, category, status, *_ = product

    if status == "Available":
        # Product is being rented
        new_status = "Rented"
    elif status == "Rented":
        # Product is being returned
        new_status = "Available"
    else:
        return {"error": f"Unknown status: {status}"}

    # Update the product's status and last_action_time
    update_product(
        product_id,
        name=name,
        tag_id=tag_id,
        category=category,
        status=new_status,
        rental_type=product[6],  # Retain current rental type
        rental_rate=product[7]   # Retain current rental rate
    )

    return {
        "product_id": product_id,
        "name": name,
        "category": category,
        "old_status": status,
        "new_status": new_status,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
