import sys
from user import User
from field_class import *
from crop import *
from database import *
from user_inventory import *

from dotenv import load_dotenv
load_dotenv("../../.env")

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
    counter = 1
    print("==== FARMERS MARKET ====")
    print("Shopkeeper: This is the current selection of items")
    rows = select_random_items(3)
    while shopping:
        print(f"You currently have ${curr_user.money}")
        counter = 1
        for row in rows:
            print(f"{counter}: {row[1]} ${row[3]} (Rarity: {row[2]})")
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
        elif shop_choice > 0 and shop_choice <= 3:
            item_to_buy = rows[shop_choice - 1]
            item_price = item_to_buy[3]
            # Users aren't able to buy an item they can't afford
            if curr_user.money < item_price:
                print("You don't have enough money to buy this item")
                continue

            print(f"You bought a {item_to_buy[1]}")
            subtract_user_money_db(item_price, curr_user.username, curr_user.password)
            curr_user.inventory.add_item(curr_user, item_to_buy[1])
            curr_user.money -= item_price
        else:
            print("Enter a valid choice!")

def is_harvestable(crop_id):
    
    crop = get_planted_crop(crop_id)
    if not crop:
        print("Enter a valid crop ID!")
        return
    
    seconds_after_planting = int(crop['seconds_after_planting'])
    total_growth_time = int(crop['total_growth_time_seconds'])
    if seconds_after_planting >= total_growth_time:
        return True
    return False

def visit_field(user_obj):
    """
    Allows the user to visit their field

    This method will show the user what is planted, what is fully grown, and the field's conditions

    Args:
        user_obj (User): The object representing the current user

    """
    global moisture_decay_rate
    global fertilizer_decay_rate

    planted_crops = get_crop_times(user_obj.username, user_obj.password)
    field_row = get_field_moisture_fertilizer(user_obj.username, user_obj.password)
    last_updated = get_last_updated(user_obj.username, user_obj.password)

    if not field_row:
        print("Your field is empty, plant some crops!")
        return

    moisture_percent = field_row['moisture_percent']
    fertilizer_percent = field_row['fertilizer_percent']

    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - last_updated).total_seconds()

    moisture_now = max(0, moisture_percent - (elapsed_seconds * moisture_decay_rate))
    fertilizer_now = max(0, fertilizer_percent - (elapsed_seconds * fertilizer_decay_rate))

    print("Your field: ")
    print(f"Moisture percent: {int(moisture_now)}  Fertilizer percent: {int(fertilizer_now)}")

    time_until_dry = moisture_percent / moisture_decay_rate
    time_until_unfertilized = fertilizer_percent / fertilizer_decay_rate
    field_death_time = last_updated + timedelta(seconds=min(time_until_dry, time_until_unfertilized))

    now = datetime.now(timezone.utc)
    effective_end_time = min(now, field_death_time)

    for crop in planted_crops:
        date_planted = crop['date_planted']
        total_growth_time = int(crop['total_growth_time_seconds'])

        growth_start_time = max(date_planted, last_updated)
        effective_growing_time = max(0, (effective_end_time - growth_start_time).total_seconds())

        if effective_growing_time >= total_growth_time:
            print(f"Crop: {crop['crop_type']} (ID: {crop['planted_crop_id']}) is ready to harvest!")
        else:
            time_remaining_seconds = total_growth_time - effective_growing_time
            print(f"Crop: {crop['crop_type']} (ID: {crop['planted_crop_id']}) is still growing!")
            print(f"time remaining (seconds): {int(time_remaining_seconds)}")


def harvest_crop_interface():
    """
    Display harvest interface and obtain user input for harvesting
    
    """

    global test_field
    global curr_user

    harvesting = True
    while harvesting:
        print("Enter 0 to exit.")
        try:
            user_input = int(input("Enter a crop's ID to harvest it: "))
        except ValueError:
            print("Enter a valid ID/choice!")
            continue
        
        if user_input == 0:
            print("Exiting the harvest interface")
            harvesting = False
            return
        
        if is_harvestable(user_input):
            crop = get_planted_crop(user_input)
            test_field.harvest_crop(curr_user, user_input)

            seed_name = crop['crop_type'] + " Seed"
            curr_user.inventory.add_item(curr_user, crop['crop_type'])
            curr_user.inventory.add_item(curr_user, seed_name)
        else:
            print("This crop is not ready to be harvested yet!")


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
    elif choice_int == 1:
        test_field.water_field(curr_user)
    elif choice_int == 2:
        test_field.fertilize_field(curr_user)
    elif choice_int == 3:
        test_field.plant_crop(curr_user, "Potato")
    elif choice_int == 4:
        visit_field(curr_user)
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
        money = user_sign_in(username, password) # If the login credentials are valid, money >= 0
        
        # Users must enter valid login credentials
        if (money >= 0):
            user_inventory = UserInventory(username, password)
            user_inventory.load_inventory()
            curr_user = User(username, password, money, user_inventory)
            num_planted, moisture_percent, fertilizer_percent  = load_user_field(curr_user.username, curr_user.password)
            test_field = Field(num_planted, moisture_percent, fertilizer_percent)
            return curr_user
        else:
            print("Invalid login credentials!")
            return None
        
    # 2 = create account
    elif choice_int == 2:
        login_list = get_login_info() # get [username, pw]
        user_inventory = UserInventory(login_list[0], login_list[1])
        user_inventory.load_inventory()
        curr_user = User(login_list[0], login_list[1], 100, user_inventory)
        insertion_successful = insert_user_to_db(curr_user.username, curr_user.password, curr_user.money)
        
        if insertion_successful:
            insert_new_user_field(curr_user.username, curr_user.password)
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