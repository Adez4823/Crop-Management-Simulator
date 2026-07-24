class User: 
    """
    Represents a user.

    Attributes:
        user_id (int): User's unique ID
        username (str): User's name 
        password (str): User's password (For the future login/sign-up)
        money    (int): User's cash amount
        inventory (UserInventory): Represents the user's inventory

    """
    def __init__(self, user_id, username='default', password='default', money=100, inventory=None):
            self.user_id = user_id
            self.username = username
            self.password = password
            self.money = money
            self.inventory = inventory

    def logout(self):
        """
        Saves the user's data to the database in order to log out safely

        """
        from database import update_field_decay

        update_field_decay(self.user_id, persist=True)


    