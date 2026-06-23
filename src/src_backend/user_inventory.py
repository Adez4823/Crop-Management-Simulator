from database import load_inventory_db
from item import Item

class UserInventory:
    def __init__(self, username, password, inventory_arr=None):
        self.username = username
        self.password = password
        self.inventory_arr = inventory_arr or []

    def load_inventory(self):
        """
        Loads the user's inventory from the database

        Creates and adds item objects to the user's inventory corresponding to what is shown in the database

        """
        self.inventory_arr = []
        rows = load_inventory_db(self.username, self.password)

        # Cannot load an empty inventory
        if not rows:
            print("Inventory currently empty")
        else:
            # Create item objects from the database rows
            for item_id, item_name, item_type, rarity, buy_price, quantity in rows:
                self.inventory_arr.append(Item(item_id, item_name, item_type, rarity, buy_price, quantity))

    def add_item(self, user_obj, item_name):
        """
        Add an item to the user's inventory

        Args:
            user_obj  (User): The User object that represents the current user
            item_name (str): The name of the item to be added to the user's inventory

        """
        from database import add_item_inventory_db, get_item_definition

        # If the item already exists in the inventory, increment it
        for item in self.inventory_arr:
            if item.item_name == item_name:
                item.quantity_item += 1

                add_item_inventory_db(user_obj.username, user_obj.password, item_name)
                print(f"You added a {item_name} to your inventory!")
                return

        # If the item doesn't exist in the user's inventory, add it
        try:
            new_item_row = get_item_definition(item_name)
        except ValueError as err:
            print(err)
            return
        
        add_item_inventory_db(user_obj.username, user_obj.password, item_name)

        item_id, name, item_type, rarity, buy_price = new_item_row
        new_item = Item(item_id, name, item_type, rarity, buy_price, 1)

        self.inventory_arr.append(new_item)
    
    def display_inventory(self):
        """
        Prints the user's inventory to the terminal

        """
        items = load_inventory_db(self.username, self.password)

        # Cannot load an empty inventory
        if not items:
            print("Inventory currently empty")
        else:
            for item in items:
                print(f"{item['item_name']}: {item['quantity']} owned. ({item['rarity']})")

    def display_seeds(self):
        """
        Displays all items that are of type 'Seed' in the user's inventory

        """

        counter = 0
        items = load_inventory_db(self.username, self.password)

        # Cannot load an empty inventory
        if not items:
            print("Inventory currently empty")

        # Print out all items of type 'Seed'
        for item in items:
            if item['item_type'] == 'Seed':
                print(f"{item['item_name']} (ID: {item['item_id']}): {item['quantity']} owned. ({item['rarity']})")
                counter += 1

        # If no seeds are found, let the user know
        if counter == 0:
            print("You don't have any seeds!")

    def remove_item(self, user_obj, name_item):
        """
        Removes an item from the user's inventory

        The item is removed/decremented in the database and removed from the inventory object

        Args:
            user_obj (User): Represents the current user
            name_item (str): The name of the object to be deleted

        """
        from database import remove_item_inventory_db

        for item in self.inventory_arr:
            if str(item.item_name).strip() == str(name_item).strip():
                # If user has multiple of an item, decrement
                if item.quantity_item > 1:
                    item.quantity_item -= 1
                # Otherwise remove completely
                else:
                    self.inventory_arr.remove(item)

                remove_item_inventory_db(user_obj.username, user_obj.password, name_item)
                return

