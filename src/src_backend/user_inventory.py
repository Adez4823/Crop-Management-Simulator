from database import load_inventory_db
from item import Item

class UserInventory:
    def __init__(self, user_id, inventory_arr=None):
        self.user_id = user_id
        self.inventory_arr = inventory_arr or []

    def load_inventory(self):
        """
        Loads the user's inventory from the database

        Creates and adds item objects to the user's inventory corresponding to what is shown in the database

        """
        self.inventory_arr = []
        rows = load_inventory_db(self.user_id)

        # Cannot load an empty inventory
        if not rows:
            print("Inventory currently empty")
        else:
            # Create item objects from the database rows
            for row in rows:
                item_id = row['item_id']
                item_name = row['item_name']
                item_type = row['item_type']
                item_rarity = row['rarity']
                item_price = row['buy_price']
                quantity_item = row['quantity']

                new_item = Item(item_id, item_name, item_type, item_rarity, item_price, quantity_item)
                self.inventory_arr.append(new_item)

    def add_item(self, item_name):
        """
        Add an item to the user's inventory

        Args:
            item_name (str): The name of the item to be added to the user's inventory

        """
        from database import add_item_inventory_db, get_item_definition

        # If the item already exists in the inventory, increment it
        for item in self.inventory_arr:
            if item.item_name == item_name:
                item.quantity_item += 1

                add_item_inventory_db(self.user_id, item_name)
                print(f"You added a {item_name} to your inventory!")
                return

        # If the item doesn't exist in the user's inventory, add it
        try:
            new_item_row = get_item_definition(item_name)
        except ValueError as err:
            print(err)
            return
        
        add_item_inventory_db(self.user_id, item_name)

        item_id, name, item_type, rarity, buy_price = new_item_row
        new_item = Item(item_id, name, item_type, rarity, buy_price, 1)

        self.inventory_arr.append(new_item)
    
    def display_inventory(self):
        """
        Prints the user's inventory to the terminal

        """
        print(f"==== INVENTORY ====")
        items = load_inventory_db(self.user_id)

        # Cannot load an empty inventory
        if not items:
            print("Inventory currently empty")
        else:
            for item in items:
                print(f"{item['item_name']}: {item['quantity']} owned. ({item['rarity']})")

    def display_seeds(self, planting_seeds=False):
        """
        Displays all items that are of type 'Seed' in the user's inventory

        """

        counter = 1
        item_id_arr = []
        items = load_inventory_db(self.user_id)

        # Cannot load an empty inventory
        if not items:
            print("Inventory currently empty")

        # Print out all items of type 'Seed'
        for item in items:
            if item['item_type'] == 'Seed':
                item_id_arr.append(item['item_id'])
                print(f"{counter}. {item['item_name']}: {item['quantity']} owned. ({item['rarity']})")
                counter += 1

        # If no seeds are found, let the user know
        if counter == 1:
            print("You don't have any seeds!")

        if planting_seeds:
            return item_id_arr

    def remove_item(self, name_item):
        """
        Removes an item from the user's inventory

        The item is removed/decremented in the database and removed from the inventory object

        Args:
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

                remove_item_inventory_db(self.user_id, name_item)
                return

