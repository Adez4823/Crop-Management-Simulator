from database import load_inventory_db, add_item_inventory_db, remove_item_inventory_db

def build_inventory(user_id):
    """
    Helper function that builds the array containing the user's inventory

    Creates and adds item objects to the user's inventory array corresponding to the db

    """
    inventory_arr = []
    rows = load_inventory_db(user_id)

    # Cannot load an empty inventory
    if not rows:
        return []
    else:
        # Create item objects from the database rows
        for row in rows:
            item_id = row['item_id']
            item_name = row['item_name']
            item_type = row['item_type']
            item_rarity = row['rarity']
            item_price = row['buy_price']
            quantity_item = row['quantity']

            inventory_arr.append({
                "item_id": item_id,
                "item_name": item_name,
                "item_type": item_type,
                "item_rarity": item_rarity,
                "item_price": item_price,
                "quantity_item": quantity_item
            })

    return inventory_arr

def load_inventory(user_id):
    """
    Loads the user's inventory from the database

    The service method that will return the user's inventory in a response for the frontend
    """
    inventory_arr = build_inventory(user_id)

    # Cannot load an empty inventory
    if not inventory_arr:
        return {
            "ok": False,
            "error": {
                "code": "INVENTORY_EMPTY",
                "message": "Inventory currently empty."
            }
        }

    return {
        "ok": True,
        "data": {
            "inventory": inventory_arr
        }
    }

def add_item(user_id, item_name):
    """
    Add an item to the user's inventory

    Args:
        user_id (int): The id of the current user
        item_name (str): The name of the item to be added to the user's inventory

    """

    add_item_result = add_item_inventory_db(user_id, item_name)


    if not add_item_result["ok"]:
        return {
            "ok": False,
            "error": {
                "code": add_item_result["error"]["code"],
                "message": add_item_result["error"]["message"]
            }
        }

    return {
        "ok": True,
        "data": {
            "inventory": build_inventory(user_id)
        }
    }

def remove_item(user_id, item_name):
    """
    Remove an item from the user's inventory

    Args:
        user_id (int): The id of the current user
        item_name (str): The name of the item to be removed from the user's inventory

    """

    remove_item_result = remove_item_inventory_db(user_id, item_name)


    if not remove_item_result["ok"]:
        return {
            "ok": False,
            "error": {
                "code": remove_item_result["error"]["code"],
                "message": remove_item_result["error"]["message"]
            }
        }

    return {
        "ok": True,
        "data": {
            "inventory": build_inventory(user_id)
        }
    }