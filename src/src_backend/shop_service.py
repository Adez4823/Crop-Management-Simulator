import config
from database import add_item_inventory_db, select_shop_items, buy_item, add_user_money_db

def get_items_in_shop():
    """
    Returns a list of items available in the shop

    The service method that will return the items available in the shop in a response for the frontend
    """
    item_rows = select_shop_items(config.NUM_ITEMS_IN_SHOP)
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

def buy_shop_item(user_id, item_name):
    """
    Allows the user to buy an item from the shop

    Args:
        user_id (int): The id of the current user
        item_name (str): The name of the item to be bought
    """

    shop_items = select_shop_items(config.NUM_ITEMS_IN_SHOP)

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
            buy_item_result = buy_item(user_id, item['item_name'])
            if not buy_item_result["ok"]:
                return {
                    "ok": False,
                    "error": {
                        "code": buy_item_result["error"]["code"],
                        "message": buy_item_result["error"]["message"]
                    }
                }
            
            return {
                "ok": True,
                "data": {
                    "user": {
                        "remaining_money": buy_item_result['data']['remaining_money']
                    },
                    "item_bought": {
                        "item_name": item_name,
                        "item_price": item['buy_price'],
                    }
                }
            }

    # Selected item not found in the shop
    return {
        "ok": False,
        "error": {
            "code": "ITEM_NOT_FOUND",
            "message": f"{item_name} is not currently available in the shop."
        }
    }


