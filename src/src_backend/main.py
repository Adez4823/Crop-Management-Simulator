import sys
from user import User
from field_class import *
from crop import *
from user_inventory import *
import requests

from dotenv import load_dotenv
load_dotenv("../../.env")

import config
from weather import get_weather_rates
from database import *

# Global Variables
running = True
test_field = Field()
curr_user = None

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
    print("5. Visit the shop")
    print("6. Visit your field")
    print("7. View your inventory")
    print("0. Exit")

def display_shop():
    """
    Display the shop and get user input

    """
    global curr_user

    shopping = True
    num_items_in_shop = 3
    counter = 1
    print("==== FARMERS MARKET ====")
    print("Shopkeeper: This is the current selection of items")
    rows = select_random_items(num_items_in_shop)
    while shopping:
        print(f"You currently have ${curr_user.money}")
        counter = 1
        for row in rows:
            print(f"{counter}: {row[1]} ${row[4]} (Rarity: {row[3]})")
            counter += 1
        
        print("0: Exit shop")

        # Users must enter a numeric value
        try:
            shop_choice = int(input("Which item would you like to buy (number): "))
        except ValueError:
            print("Enter a valid choice!")
            continue
        
        # Users can exit the shot by entering 0
        if shop_choice == 0:
            print("Exiting shop")
            shopping = False
            break
        # Users must enter a valid choice
        elif shop_choice > 0 and shop_choice <= num_items_in_shop:
            item_to_buy = rows[shop_choice - 1]
            item_price = item_to_buy[4]
            # Users aren't able to buy an item they can't afford
            if curr_user.money < item_price:
                print("You don't have enough money to buy this item")
                continue

            print(f"You bought a {item_to_buy[1]}")
            subtract_user_money_db(item_price, curr_user.user_id)
            curr_user.inventory.add_item(item_to_buy[1])
            curr_user.money -= item_price
        else:
            print("Enter a valid choice!")

def is_harvestable(crop_id):
    """
    Determines if a crop is ready to harvest

    Args:
        crop_id (int): The id that corresponds to the planted crop
        crop_id_arr (array): The array containing all the planted crop ids in the user's field

    Returns:
        boolean: True if crop is ready to harvest

    """
    global curr_user

    update_field_decay(curr_user.user_id, persist=True)
    # Get the row corresponding to the crop id
    crop = get_planted_crop(crop_id)
    # User's cannot enter an invalid id
    if not crop:
        print("Enter a valid crop ID!")
        return
    
    # Determine the time that has passed after a crop has been planted
    total_time_grown = int(crop['total_time_grown'])
    total_growth_time = int(crop['total_growth_time_seconds'])
    
    # Crops cannot be harvested if they have not grown their full time
    if total_time_grown >= total_growth_time:
        return True
    return False

def visit_field(user_obj, harvesting_crop=False):
    """
    Allows the user to visit their field


    This method will show the user what is planted, what is fully grown, and the field's conditions


    Args:
        user_obj (User): The object representing the current user


    """


    field_status = test_field.get_field_status(user_obj)


    print(f"Your field: ")
    print(f"Moisture: {int(field_status['moisture'])} Fertilizer: {int(field_status['fertilizer'])}")
    print()

    counter = 1
    crop_id_arr = []

    for crop in field_status['crops']:
        # Store the crop id in an array
        crop_id_arr.append(crop['planted_crop_id'])

        if crop['ready_to_harvest']:
            print(f"{counter}. {crop['crop_type']} is ready to harvest!")
            print()
            counter += 1
        else:
            print(f"{counter}. {crop['crop_type']} is still growing!")
            print(f"Time Remaining (seconds): {int(crop['time_until_grown'])}")
            print()
            counter += 1

    if harvesting_crop:
        return crop_id_arr


def harvest_crop_interface():
    """
    Display harvest interface and obtain user input for harvesting
    
    """

    global test_field
    global curr_user

    # Obtain the crop id array from the visit_field method
    crop_id_arr = visit_field(curr_user, harvesting_crop=True)

    harvesting = True
    while harvesting:
        print("Enter 0 to exit.")
        try:
            user_input = int(input("Enter the crop # to harvest it: "))
        except ValueError:
            print("Enter a valid choice!")
            continue
        
        if user_input == 0:
            print("Exiting the harvest interface")
            harvesting = False
            return
        
        try:
            crop_id_corresponding_to_input = crop_id_arr[user_input - 1]
        except IndexError:
            print("Enter a valid choice!")
            continue

        if is_harvestable(crop_id_corresponding_to_input):
            crop = get_planted_crop(crop_id_corresponding_to_input)
            test_field.harvest_crop(curr_user, crop_id_corresponding_to_input)

            seed_name = crop['crop_type'] + " Seed"
            curr_user.inventory.add_item(crop['crop_type'])
            curr_user.inventory.add_item(seed_name)
        else:
            print("This crop is not ready to be harvested yet!")

def plant_crop_interface(user_obj):
    """
    Displays the planting interface and handle the user's choice

    Args:
        user_obj (User): The user object representing the current user

    """

    global curr_user
    global test_field

    planting = True
    while planting:
        curr_user.inventory.display_seeds()

        print("0. Exit")
        # User's must enter in a valid seed id
        try:
            user_input = int(input("Which seed would you like to plant (enter ID): "))
        except ValueError:
            print("Enter a valid choice!")
            continue
        # Exiting the plant_crop_interface
        if user_input == 0:
            print("Exiting...")
            planting = False
            return
        else:
            seed = get_seed_item(user_input)
            if not seed:
                print("Enter a valid choice!")
                return
            plant_type = seed['item_name'].replace(" Seed", "") 
            # Plant the corresponding crop
            test_field.plant_crop(curr_user, plant_type)
            # Remove the seed object
            curr_user.inventory.remove_item(seed['item_name'])


def handle_choice(choice):
    """
    Perform actions according to the user's choice in the main interface

    Args:
        choice (str): The user's choice as a string

    """
    global curr_user

    choice_int = str_to_int(choice)

    if choice_int == 0:
        global running
        running = False
        curr_user.logout()
        print("Exiting...")
    elif choice_int == 1:
        test_field.water_field(curr_user)
    elif choice_int == 2:
        test_field.fertilize_field(curr_user)
    elif choice_int == 3:
        plant_crop_interface(curr_user)
    elif choice_int == 4:
        harvest_crop_interface()
    elif choice_int == 5:
        display_shop()
    elif choice_int == 6:
        visit_field(curr_user)
    elif choice_int == 7:
        curr_user.inventory.display_inventory()
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
    global test_field

    # 1 = login
    if choice_int == 1:
        login_list = get_login_info() # get login credentials
        username = login_list[0]
        password = login_list[1]

        login_result = user_sign_in(username, password)

        if login_result is None:
            print("Invalid login credentials!")
            return None

        money, user_id = login_result
        
        # Users must enter valid login credentials
        if (money >= 0 and user_id is not None):
            user_inventory = UserInventory(user_id)
            user_inventory.load_inventory()
            curr_user = User(user_id, username, password, money, user_inventory)
            num_planted, moisture_percent, fertilizer_percent  = load_user_field(curr_user.user_id)
            test_field = Field(num_planted, moisture_percent, fertilizer_percent)
            return curr_user
        else:
            print("Invalid login credentials!")
            return None
        
    # 2 = create account
    elif choice_int == 2:
        login_list = get_login_info() # get [username, pw]
        username = login_list[0]
        password = login_list[1]
        user_id = insert_user_to_db(username, password, 100)
        if user_id is not None:
            user_inventory = UserInventory(user_id)
            user_inventory.load_inventory()
            curr_user = User(user_id, username, password, 100, user_inventory)
            insert_new_user_field(curr_user.user_id)
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
    global curr_user
    global test_field

    try:
        config.set_moisture_decay_rate(
            get_weather_rates(config.CURRENT_CITY)
        )
    except requests.RequestException:
        print("Weather API unavailable. Using default decay rate.")

    create_tables()
    curr_user = login_signup_interface()
    print(f"Test field num {test_field.num_plants}")


    while (running): # Game loop
        display_interface(curr_user)

        print("Enter your choice: ", end="") # Get user input
        choice = input().strip()
        handle_choice(choice)    


if __name__ == "__main__":
    main()