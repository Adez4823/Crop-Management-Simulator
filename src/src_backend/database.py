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
        cur.execute(f.read())

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