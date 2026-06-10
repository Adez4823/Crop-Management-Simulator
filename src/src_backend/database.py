import psycopg
import os

def connect_to_db():
    """
    Connects to the postgres DB

    Returns:
        Connection: The connection object to the database
    """
    
    db_connection = psycopg.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return db_connection

def create_tables():
    """
    Create db tables if they don't exist, populate crop types

    """
    conn = connect_to_db()
    cur = conn.cursor()


    path_schema = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(path_schema, "r") as f:
        sql_statements = f.read()

    for statement in sql_statements.split(";"):
        if statement.strip():
            cur.execute(statement)

    # Initialize the crop_types table to default values
    cur.execute("""
        INSERT INTO crop_types 
        (crop_type_id, crop_type, total_growth_time_seconds, water_requirement, sell_price, seed_price) 
        VALUES 
                (1, 'Potato', 200, 40, 100, 50),
                (2, 'Leek', 200, 70, 70, 20),
                (3, 'Corn', 200, 70, 70, 20),
                (4, 'Celery', 200, 70, 70, 20),
                (5, 'Beans', 200, 70, 70, 20),
                (6, 'Brussel Sprouts', 200, 70, 70, 20)
                ON CONFLICT DO NOTHING;
    """)

    # Initialize the item definition table to default values
    cur.execute("""
        INSERT INTO items 
        (item_id, item_name, rarity, buy_price) 
        VALUES 
                (1, 'Potato Seed', 'Common', 50),
                (2, 'Leek Seed', 'Common', 20),
                (3, 'Corn Seed', 'Uncommon', 20),
                (4, 'Celery Seed', 'Uncommon', 20),
                (5, 'Beans Seed', 'Uncommon', 20),
                (6, 'Brussel Sprout', 'Rare', 20)
                ON CONFLICT DO NOTHING;
    """)

    conn.commit()
    cur.close()
    conn.close()

def insert_user_to_db(username, password, money):
    """
    Inserts a user into the user table of the database

    Args:
        user_obj (User): The user object to be inserted

    Raises:s
        UniqueViolation: If the username is already taken
    
    Returns:
        True/False (boolean): True if the user was inserted successfully

    """

    conn = connect_to_db()
    cur = conn.cursor()
    
    # User's cannot use the same username as another
    try:
        cur.execute(
            """
            INSERT INTO users (username, password, money)
            VALUES (%s, %s, %s)
            """,
            (username, password, money)
        )
        conn.commit()
        print("User sucessfully inserted to DB")
        return True
    # Don't update DB if there's an exception
    except psycopg.errors.UniqueViolation as e:
        conn.rollback()
        print("Username already exists!")
        return False

    finally:
        cur.close()
        conn.close()

def user_sign_in(username, pw):
    """
    Tries to get the user's info given username + password

    The method will return -1 if the user does not exist within the database

    Args:
        username (str): The user's username that was inputted to the login interface
        pw       (str): The user's password that was inputted to the login interface
    
    Returns:
        money    (int): The user's amount of money

    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT money FROM users WHERE username = %s AND password = %s;", (username, pw))

        user_row = cur.fetchone()

        # Users must provide valid login credentials
        if user_row is None:
            return -1 # -1 signifies credentials not found
        else:
            money = user_row[0]
            return money
    
    # Ensure connection is always closed
    finally:
        cur.close()
        conn.close()

def insert_new_user_field(username, password):
    """
    Create a new entry into the database, containing default values for the user's new field.

    This method is used right after account creation in order to initialize a field for the user as well as initialize the planted crops within the field.

    Args:
        username (str): The username of the current user
        password (str): The password of the current user

    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE username = %s and password = %s;", (username, password))

    user_row = cur.fetchone()
    user_id = user_row[0]

    # Create default fields entry
    cur.execute("""
    INSERT INTO fields 
    (user_id, num_planted, moisture_percent, fertilizer_percent) 
    VALUES 
            (%s, %s, %s, %s);""", 
            (user_id, 0, 0, 0) 
    )
    conn.commit()
    cur.close()
    conn.close()

def plant_crop_db(username, password, crop_name):
    """
    Allows the user to plant a crop by updating the DB

    Increments the fields table's num_planted and inserts a row to the crops_planted table

    Args:
        username (str): The username of the current user
        password (str): The password of the current user
        crop_name (str): The name of the crop to be planted

    """
    conn = connect_to_db()
    cur = conn.cursor()

    # Get user_id
    cur.execute("SELECT user_id FROM users WHERE username = %s AND password = %s;", (username, password))
    user_row = cur.fetchone()
    user_id = user_row[0]

    # Get total growth time given the crop name
    cur.execute("SELECT total_growth_time_seconds FROM crop_types WHERE crop_type = %s;", (crop_name,))
    crop_row = cur.fetchone()
    total_growth_time = crop_row[0]

    # Increment num_planted in the player's field and get field_id
    cur.execute("""UPDATE fields 
                SET num_planted = num_planted + %s WHERE user_id = %s
                RETURNING field_id;""", (1, user_id))
    
    field_id = cur.fetchone()[0]
    
    # Add row to planted_crops table
    cur.execute("""
        INSERT INTO planted_crops 
        (field_id, crop_type, total_growth_time_seconds) 
        VALUES 
            (%s, %s, %s);
    """, (field_id, crop_name, total_growth_time))

    conn.commit()
    cur.close()
    conn.close()

def load_user_field(username, password):
    """
    Query the database to get the field corresponding to the user

    Args:
        username (str): The username of the current user
        password (str): The password of the current user
    
    Returns:
        Field: The field object that corresponds to the current user

    """

    conn = connect_to_db()
    cur = conn.cursor()

    # Get user ID
    cur.execute("SELECT user_id FROM users WHERE username = %s AND password = %s;", (username, password))
    user_row = cur.fetchone()
    user_id = user_row[0]

    # Get the corresponding field row
    cur.execute("SELECT * FROM fields WHERE user_id = %s;", (user_id,))
    field_row = cur.fetchone()
    num_planted = field_row[2]
    moisture_percent = field_row[3]
    fertilizer_percent = field_row[4]

    cur.close()
    conn.close()

    # Return the data needed to construct the user's field as a tuple
    return num_planted, moisture_percent, fertilizer_percent


def harvest_crop_db(username, password, crop_name):
    """
    Allows the user to harvest a crop by updating the DB

    Decrements the fields table's num_planted and deletes the corresponding row in the crops_planted table

    Args:
        username  (str): Current user's username
        password  (str): Current user's password
        crop_name (str): The name of the crop to be planted

    """
    conn = connect_to_db()
    cur = conn.cursor()

    # Get user_id
    cur.execute("SELECT user_id FROM users WHERE username = %s AND password = %s;", (username, password))
    user_row = cur.fetchone()
    user_id = user_row[0]   

    # Increment num_planted in the player's field and get field_id
    cur.execute("""UPDATE fields 
                SET num_planted = num_planted - %s WHERE user_id = %s
                RETURNING field_id;""", (1, user_id))
    
    field_id = cur.fetchone()[0]
    
    # Delete corresponding planted_crops table
    cur.execute("""
        DELETE FROM planted_crops
        WHERE ctid IN (
            SELECT ctid
            FROM planted_crops
            WHERE field_id = %s
            AND crop_type = %s
            LIMIT 1
        );
    """, (field_id, crop_name))

    ###
    ### IN THE FUTURE THIS METHOD MUST UTILIZE THE USER INVENTORY DATABSE
    ###

    conn.commit()
    cur.close()
    conn.close() 

def load_inventory_db(username, password):
    """
    Query the database for all items the current user owns

    Args:
        user_id (int): Represents the user's unique ID

    Returns:
        rows (list[tuple]): Represents the owned items and the quantity of each item

    """

    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("""SELECT user_inventories.item_id, items.item_name, items.rarity, items.buy_price, user_inventories.quantity
                FROM user_inventories JOIN items ON items.item_id = user_inventories.item_id
                WHERE user_inventories.username = %s AND user_inventories.password = %s
            """, (username, password))

    rows = cur.fetchall()

    cur.close()
    conn.close() 

    return rows

def get_item_id(item_name):
    """
    Get the item's id

    Args:
        item_name (str): Name of the item

    Returns:
        item_id   (int): The number corresponding to the item 

    Raises:
        ValueError: If the item doesn't exist within the item definition table

    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT item_id FROM items WHERE item_name = %s;", (item_name,))
    item_row = cur.fetchone()

    if not item_row:
        cur.close()
        conn.close()
        raise ValueError(f"Item '{item_name}' not found in items table.")
    
    else:
        item_id = item_row[0]

    cur.close()
    conn.close()

    return item_id

def get_item_definition(item_name):
    """
    Get the item's price

    Args:
        item_name (str): Name of the item

    Returns:
        item_row  (tuple): The tuple representing the item

    Raises:
        ValueError: If the item doesn't exist within the item definition table

    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM items WHERE item_name = %s",  (item_name,))
    item_row = cur.fetchone()

    if not item_row:
        cur.close()
        conn.close()
        raise ValueError(f"Item '{item_name}' not found in items table.")
    

    cur.close()
    conn.close()

    return item_row

def add_item_inventory_db(username, password, item_name):
    """
    Allows the user to buy items

    Adds an item to the user's inventory in the database

    Args:
        username (str): The username of the current user
        password (str): The password of the current user
        item_name (str): The name of the item that is to be added to the user's inventory

    Raises:
        ValueError: If the item_name doesn't match an item in the item definitions table (can't happen at this moment, but added for flexibility/redundancy)
    """
    conn = connect_to_db()
    cur = conn.cursor()

    item_id = get_item_id(item_name)

    cur.execute("SELECT * FROM user_inventories WHERE username = %s AND password = %s AND item_id = %s", (username, password, item_id))

    if cur.fetchone():
        # Increment item in the player's inventory if they already have it
        cur.execute("""UPDATE user_inventories 
                    SET quantity = quantity + %s WHERE item_id = %s AND username = %s AND password = %s;
                    """, (1, item_id, username, password))
    else:
        # The player doesn't have this item, insert a new row
        cur.execute("""INSERT INTO user_inventories
                        (username, password, item_id, quantity) 
                        VALUES 
                            (%s, %s, %s, %s);
                    """, (username, password, item_id, 1))

    conn.commit()
    cur.close()
    conn.close()

def select_random_items(num_items):
    """
    Select x random rows from the items table

    Args:
        num_items (int): number of items to select

    Returns:
        List[tuple]: a list of tuples representing each item

    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM items ORDER BY RANDOM() LIMIT %s;", (num_items,))
    rows = cur.fetchall()

    if not rows:
        print("No items exist! (DB error)")

    cur.close()
    conn.close()

    return rows

def subtract_user_money_db(amount, username, password):
    """
    Subtracts an amount of money from the user's row in the database

    Args:
        amount   (int): The value to subtract
        username (str): The string representing the current user's name
        password (str): The string representing the current user's passwor
    """
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET money = money - %s WHERE username = %s AND password = %s;", 
                (amount, username, password))

    conn.commit()
    cur.close()
    conn.close()