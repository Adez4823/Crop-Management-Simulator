import sys
from user import User
from field import *
from crop import *
from database import *

from dotenv import load_dotenv
load_dotenv("../../.env")

# Global Variables
running = True
test_field = Field()

def get_login_info():
    """
    Get the user's username and password from stdin

    Returns:
        List: The list containing the inputted username and password

    """
    print("Enter your username: ", end="")
    username = input().strip()
    print("Enter your password: ", end = "")
    password = input().strip()
    print("")

    login_list = [username, password]

    # Create a user object and return it
    return login_list

def display_interface(current_user):
    """
    Displays the interface detailing how to perform certain actions to the terminal

    Args:
        current_user (User): The user object representing the current user

    """
    print(f"==== MAIN MENU ==== (logged in as {current_user.username})")
    print("1. Water your field")
    print("2. Fertilize your field")
    print("3. Plant a crop")
    print("4. Harvest a crop")
    print("0. Exit")

def handle_choice(choice):
    """
    Perform actions according to the user's choice

    Args:
        choice (str): The user's choice as a string

    """

    choice_int = str_to_int(choice)

    if choice_int == 0:
        global running
        running = False
    elif choice_int == 1:
        test_field.water_field()
    elif choice_int == 2:
        test_field.fertilize_field()
    elif choice_int == 3:
        test_field.plant_crop("Corn")
    elif choice_int == 4:
        test_field.harvest_crop()
    else: # Users must enter a valid choice
        print("Please enter one of the numerical choices")
    print("") # Extra newline for space

def str_to_int(choice):
    """
    Converts a numeric string to an int

    Args:
        choice (str): The user's choice as a string
    
    Returns:
        int: The user's choice as an int

    """
    # Users cannot input letters as a choice
    if not choice.isdigit():
        print("Please enter one of the numerical choices")
        return
    else:
        choice_int = int(choice)
        return choice_int

def handle_login_choice(choice_int):
    """
    Handles the login choice of the user, either login/signup

    Args:
        choice_int (int): The user's choice as an int

    Returns:
        User: The User object of the current user
        None: Returned if invalid login/signup credentials are provided

    """

    # 1 = login
    if choice_int == 1:
        login_list = get_login_info() # get login credentials
        username = login_list[0]
        password = login_list[1]
        money = user_sign_in(username, password) # If the login credentials are valid, money >= 0
        
        # Users must enter valid login credentials
        if (money >= 0):
            curr_user = User(username, password, money)
            return curr_user
        else:
            print("Invalid login credentials!")
            return None
        
    # 2 = create account
    elif choice_int == 2:
        login_list = get_login_info() # get [username, pw]
        curr_user = User(login_list[0], login_list[1])
        insertion_successfull = insert_user_to_db(curr_user)
        
        if insertion_successfull:
            return curr_user
        else:
            return None

    else:
        print("Please enter either 1 or 2.")
        return None


def login_signup_interface():
    """
    Displays the login interface 

    Returns:
        User: The user object that represents the user who just logged in/signed up

    """

    logging = True

    # Display login/signup interface
    while logging: 
        print("1. Login")
        print("2. Create Account")
        print("What do you want to do (enter a number): ", end="")

        # Get user input
        choice = input().strip()
        choice_int = str_to_int(choice) # Convert input to int

        # Handle user input
        logged_user = handle_login_choice(choice_int)

        # User must successfully login or create an account or this interface will be displayed indefinitely
        if logged_user is not None:
            break
    
    return logged_user

def main():
    """
    Main game logic and loop

    """
    create_tables()
    current_user = login_signup_interface()

    while (running): # Game loop
        display_interface(current_user)

        print("Enter your choice: ", end="") # Get user input
        choice = input().strip()
        handle_choice(choice)

        


if __name__ == "__main__":
    main()

