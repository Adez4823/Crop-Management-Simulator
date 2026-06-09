from database import load_inventory_db
from item import Item

class UserInventory:
    def __init__(self, username, password, inventory_arr=None):
        self.username = username
        self.password = password
        self.inventory_arr = inventory_arr or []

    def load_inventory(self):
        self.inventory_arr = []
        rows = load_inventory_db(self.username, self.password)

        # Cannot load an empty inventory
        if not rows:
            print("Inventory currently empty")
        else:
            for item_id, item_name, rarity, buy_price, quantity in rows:
                self.inventory_arr.append(Item(item_id, item_name, rarity, buy_price, quantity))

    def add_item(self, user_obj, item_name):
        """
        Add an item to the user's inventory

        Args:
            user_obj  (User): The User object that represents the current user
            item_name (str): The name of the item to be added to the user's inventory

        """
        from database import add_item_inventory_db, get_item_definition

        for item in self.inventory_arr:
            if item.item_name == item_name:
                item.quantity_item += 1

                add_item_inventory_db(user_obj.username, user_obj.password, item_name)
                print(f"You added a {item_name} to your inventory!")
                return

        try:
            new_item_row = get_item_definition(item_name)
        except ValueError as err:
            print(err)
            return
        
        add_item_inventory_db(user_obj.username, user_obj.password, item_name)

        item_id, name, rarity, buy_price = new_item_row
        new_item = Item(item_id, name, rarity, buy_price, 1)

        self.inventory_arr.append(new_item)
