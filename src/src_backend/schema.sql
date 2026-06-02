-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    username VARCHAR(255) NOT NULL UNIQUE, 
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS fields (
    field_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    user_id INT NOT NULL, 
    num_planted INT NOT NULL, 
    moisture_percent INT NOT NULL, 
    fertilizer_percent INT NOT NULL, 
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS planted_crops (
    planted_crop_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    field_id INT NOT NULL, 
    crop_type VARCHAR(32) NOT NULL, 
    date_planted DATE NOT NULL, 
    total_growth_time_seconds INT, 
    FOREIGN KEY(field_id) REFERENCES fields(field_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS crop_types (
    crop_type_id INT NOT NULL, 
    crop_type VARCHAR(32) NOT NULL UNIQUE, 
    water_requirement INT NOT NULL, 
    total_growth_time_seconds INT NOT NULL, 
    sell_price INT NOT NULL, 
    seed_price INT NOT NULL, 
    PRIMARY KEY(crop_type_id)
);