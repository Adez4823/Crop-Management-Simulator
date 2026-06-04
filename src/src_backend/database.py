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

    conn.commit()
    cur.close()
    conn.close()

def insert_user_to_db(user_obj):
    """
    Inserts a user into the user table of the database

    Args:
        user_obj (User): The user object to be inserted

    Raises:
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
            (user_obj.username, user_obj.password, user_obj.money)
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

    Raises:
        Exception: If there is something wrong with the DB
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
        
    # Close connection in the case of an exception
    finally:
        cur.close()
        conn.close()

def insert_new_user_field(username, password):
    """
    Create a new entry into the database, containing default values for the user's new field.

    This method is used right after account creation in order to initialize a field for the user as well as initialize the planted crops within the field.

    Args:
        User: The User object that represents the current user

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
        user_obj (User): Represents the current user
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
    
    result = cur.fetchone()
    field_id = result[0] if result else None
    
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
        user_obj (User): Represents the current user
    
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

    # Return the data needed to construct the user's field
    return num_planted, moisture_percent, fertilizer_percent
