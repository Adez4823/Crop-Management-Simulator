class User: 
    """
    Represents a user.

    Attributes:
        username (str): User's name 
        password (str): User's password (For the future login/sign-up)
        money    (int): User's cash amount

    """
    def __init__(self, username='default', password='default', money=100):
            self.username = username
            self.password = password
            self.money = money