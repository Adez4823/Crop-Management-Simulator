class User: 
    """
    Represents a user.

    Attributes:
        user_id (int): A unique, generated ID for a user (To be used in the SQL database)
        username (str): User's name 
        password (str): User's password (For the future login/sign-up)

    """
    def __init__(self, user_id, username, password):
            self.user_id = user_id
            self.username = username
            self.password = password