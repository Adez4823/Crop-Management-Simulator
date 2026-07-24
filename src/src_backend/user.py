class User: 
    """
    Represents a user.

    Attributes:
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

    