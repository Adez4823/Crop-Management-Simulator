from datetime import datetime, timezone, timedelta
from config import MOISTURE_DECAY_RATE, FERTILIZER_DECAY_RATE

class Field:
    """
    Represents a user's field.

    Contains information on the player's field and allows the user to manage their field's condition.

    Attributes:
        num_plants (int): The number of crops planted in the field.
        moisture_percent (int): Represents the how wet/dry the field is as a percentage.
        fertilizer_percent (int): Represents how fertilized the field is as a percentage

    """

    def __init__(self, num_plants=0, moisture_percent=0, fertilizer_percent=0):
        self.num_plants = num_plants
        self.moisture_percent = moisture_percent
        self.fertilizer_percent = fertilizer_percent

    def water_field(self, user_obj):
        """
        Add water to the field.

        Adds 10 to the field's moisture, given the field is not fully watered.

        Args:
            user_obj (User): User object representing the current user

        """

        from database import water_field_db, update_field_decay


        moisture_after_decay, fertilizer_after_decay = update_field_decay(user_obj.user_id, persist=False)

        self.moisture_percent = moisture_after_decay
        self.fertilizer_percent = fertilizer_after_decay
        # Users can only water their field if it is not fully watered.
        if self.moisture_percent >= 100:
            print("Your field is already completely watered")
        else:
            self.moisture_percent += 10
            print(f"You watered your field, its moisture content is now {self.moisture_percent}")
            water_field_db(user_obj.user_id)

    def fertilize_field(self, user_obj):
        """
        Add fertilizer to the field.

        Adds 20 to the field's fertilizer percentage given the field is less than 80% fertilized.

        Args:
            user_obj (User): User object representing the current user
        """
        from database import fertilize_field_db, update_field_decay

        # Users can only fertilize their field it is 80% fertilized or less
        moisture_after_decay, fertilizer_after_decay = update_field_decay(user_obj.user_id, persist=False)

        self.moisture_percent = moisture_after_decay
        self.fertilizer_percent = fertilizer_after_decay

        if self.fertilizer_percent > 80:
            print("You cannot fertilize right now (too much fertilizer)!")
        else:
            self.fertilizer_percent += 20
            print(f"You added fertilzer to your field, its fertilizer percentage is now {self.fertilizer_percent}")
            fertilize_field_db(user_obj.user_id)

    
    def plant_crop(self, user_obj, plant_type):
        """
        Plant a crop in the field.

        Args:
            user_obj  (User): The User object that represents the current user
            plant_type (str): The type of crop to be planted.

        """
        from database import plant_crop_db

        # Users cannot plant crops if their field is full
        if self.num_plants == 100:
            print("Your field is full, harvest some crops before planting more!")
        else:
            self.num_plants = self.num_plants + 1
            plant_crop_db(user_obj.user_id, plant_type)
            print(f"You planted a {plant_type} crop in your field! There are now {self.num_plants} in your field.")

    def harvest_crop(self, user_obj, planted_crop_id):
        """
        Harvest a fully grown crop

        Args:
            planted_crop_id (int): The id of the crop to be harvested
        """
        from database import harvest_crop_db

        # Users cannot harvest from an empty field
        if self.num_plants <= 0:
            print("There are no plants to harvest!")
        else:
            self.num_plants = self.num_plants - 1
            harvest_crop_db(user_obj.user_id, planted_crop_id)


    def get_field_status(self, user_obj):
        from database import get_field_data
        from database import get_planted_crops

        field_data = get_field_data(user_obj.user_id)


        crops = get_planted_crops(user_obj.user_id)


        moisture_percent = field_data['moisture_percent']
        fertilizer_percent = field_data['fertilizer_percent']
        date_until_no_growth = field_data['date_until_no_growth']
        last_updated = field_data['last_updated']

        now = datetime.now(timezone.utc)

        elapsed_seconds = (now - last_updated).total_seconds()

        # Calculate the seconds since last_updated where crop growth was possible
        if now <= date_until_no_growth:
            effective_growth_seconds = (now - last_updated).total_seconds()
        else:
            effective_growth_seconds = (date_until_no_growth - last_updated).total_seconds()

        # Predict the current moisture/fertilizer based off time passed
        predicted_moisture_now = max(0, moisture_percent - (elapsed_seconds * MOISTURE_DECAY_RATE))
        predicted_fertilizer_now = max(0, fertilizer_percent - (elapsed_seconds * FERTILIZER_DECAY_RATE))

        crop_info = []


        for crop in crops:
            time_grown = crop['total_time_grown'] + effective_growth_seconds

            ready_to_harvest = time_grown >= crop["total_growth_time_seconds"]

            crop_info.append({
                "planted_crop_id": crop["planted_crop_id"],
                "crop_type": crop["crop_type"],
                "ready_to_harvest": ready_to_harvest,
                "time_grown": time_grown,
                "time_until_grown": max(0, crop["total_growth_time_seconds"] - time_grown)
            })


        return {
            "moisture": predicted_moisture_now,
            "fertilizer": predicted_fertilizer_now,
            "crops": crop_info
        }
