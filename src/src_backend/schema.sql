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
    moisture_percent FLOAT NOT NULL, 
    fertilizer_percent FLOAT NOT NULL, 
    last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    date_until_no_growth TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Planted crops table
CREATE TABLE IF NOT EXISTS planted_crops (
    planted_crop_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    field_id INT NOT NULL, 
    crop_type VARCHAR(32) NOT NULL, 
    date_planted TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    total_time_grown INT NOT NULL,
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

-- Item definition table
CREATE TABLE IF NOT EXISTS items (
    item_id INT NOT NULL, 
    item_name VARCHAR(32) NOT NULL UNIQUE, 
    rarity VARCHAR(32) NOT NULL, 
    buy_price INT NOT NULL, 
    PRIMARY KEY(item_id)
);

-- User inventory table
CREATE TABLE IF NOT EXISTS user_inventories (
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    item_id INT NOT NULL, 
    quantity INT NOT NULL,

    -- Ensure that items will stack
    PRIMARY KEY(username, item_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
);