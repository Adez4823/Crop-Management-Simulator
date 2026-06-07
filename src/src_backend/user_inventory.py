from database import load_inventory_db
from item import Item

class UserInventory:
    def __init__(self, username, password, inventory=None):
        self.username = username
        self.password = password
        self.inventory = inventory or []

    def load_inventory(self):
        self.inventory = []
        rows = load_inventory_db(self.username, self.password)

        # Cannot load an empty inventory
        if not rows:
            print("Inventory currently empty")
        else:
            for item_id, item_name, rarity, buy_price, quantity in rows:
                self.inventory.append(Item(item_id, item_name, rarity, buy_price, quantity))