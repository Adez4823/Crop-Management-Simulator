import config
from database import add_item_inventory_db, select_random_items, subtract_user_money_db

def get_items_in_shop():
    """
    Returns a list of items available in the shop

    The service method that will return the items available in the shop in a response for the frontend
    """
    item_rows = select_random_items(config.NUM_ITEMS_IN_SHOP)
    shop_items = []

    if not item_rows:
        return {
            "ok": False,
            "error": {
                "code": "SHOP_EMPTY",
                "message": "Shop currently empty."
            }
        }

    for item in item_rows:
        item_id = item['item_id']
        item_name = item['item_name']
        item_type = item['item_type']
        rarity = item['rarity']
        buy_price = item['buy_price']

        shop_items.append({
            "item_id": item_id,
            "item_name": item_name,
            "item_type": item_type,
            "rarity": rarity,
            "item_price": buy_price
        })

    return {
        "ok": True,
        "data": {
            "shop_items": shop_items
        }
    }

def buy_item(user_id, item_name):
    """
    Allows the user to buy an item from the shop

    Args:
        user_id (int): The id of the current user
        item_name (str): The name of the item to be bought
    """

    shop_items = select_random_items(config.NUM_ITEMS_IN_SHOP)

    if not shop_items:
        return {
            "ok": False,
            "error": {
                "code": "SHOP_EMPTY",
                "message": "Shop currently empty."
            }
        }
    
    for item in shop_items:
        if item['item_name'] == item_name:
            subtract_money_result = subtract_user_money_db(user_id, item['buy_price'])
            if not subtract_money_result["ok"]:
                return {
                    "ok": False,
                    "error": {
                        "code": subtract_money_result["error"]["code"],
                        "message": subtract_money_result["error"]["message"]
                    }
                }
            
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
                    "user": {
                        "remaining_money": subtract_money_result['data']['remaining_money']
                    },
                    "item_bought": {
                        "item_name": item_name,
                        "item_price": item['buy_price'],
                    }
                }
            }
    return {
        "ok": False,
        "error": {
            "code": "ITEM_NOT_FOUND",
            "message": f"{item_name} is not currently available in the shop."
        }
    }


