import sys
from user import User
from field import *
from crop import *

# Global Variables
running = True
test_field = Field()

def get_login_info():
    """
    Get the user's username and password from stdin

    Returns:
        User: The user object containing the information obtained from stdin

    """
    print("Enter your username: ", end="")
    user_id = 1
    username = input().strip()
    print("Enter your password: ", end = "")
    password = input().strip()
    print("")

    # Create a user object and return it
    test_user = User(user_id, username, password)
    return test_user

def display_interface(current_user):
    """
    Displays the interface detailing how to perform certain actions to the terminal

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

    """
    # Users cannot input letters as a choice
    if not choice.isdigit():
        print("Please enter one of the numerical choices")
        return
    else:
        choice_int = int(choice)

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


def main():
    """
    Main game logic and loop

    """

    # Skeleton login for now, will be changed as the login feature is completed
    current_user = get_login_info()

    while (running): # Game loop
        display_interface(current_user)

        print("Enter your choice: ", end="") # Get user input
        choice = input().strip()
        handle_choice(choice)

        


if __name__ == "__main__":
    main()

