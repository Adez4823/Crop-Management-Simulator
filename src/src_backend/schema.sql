-- Schema is in PostgreSQL version 18

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY, 
    username VARCHAR(255) NOT NULL, 
    password VARCHAR(255) NOT NULL, 
    money INT NOT NULL,
    CONSTRAINT duplicate_username UNIQUE (username)
);

-- Fields table
CREATE TABLE IF NOT EXISTS fields (
    field_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    user_id INT NOT NULL, 
    num_planted INT NOT NULL, 
    moisture_percent INT NOT NULL, 
    fertilizer_percent INT NOT NULL, 
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Planted crops table
CREATE TABLE IF NOT EXISTS planted_crops (
    planted_crop_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    field_id INT NOT NULL, 
    crop_type VARCHAR(32) NOT NULL, 
    date_planted DATE NOT NULL, 
    total_growth_time_seconds INT, 
    FOREIGN KEY(field_id) REFERENCES fields(field_id) ON DELETE CASCADE
);

-- Crop types table
CREATE TABLE IF NOT EXISTS crop_types (
    crop_type_id INT NOT NULL, 
    crop_type VARCHAR(32) NOT NULL UNIQUE, 
    water_requirement INT NOT NULL, 
    total_growth_time_seconds INT NOT NULL, 
    sell_price INT NOT NULL, 
    seed_price INT NOT NULL, 
    PRIMARY KEY(crop_type_id)
);

-- User inventory table
CREATE TABLE IF NOT EXISTS user_inventory (
    user_id INT NOT NULL,
    inv_item_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    total_items INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);