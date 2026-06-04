from database import *

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

    def water_field(self):
        """
        Add water to the field.

        Adds 10 to the field's moisture, given the field is not fully watered.
        """

        # Users can only water their field if it is not fully watered.
        if self.moisture_percent >= 100:
            print("Your field is already completely watered")
        else:
            self.moisture_percent += 10
            print(f"You watered your field, its moisture content is now {self.moisture_percent}")

    def fertilize_field(self):
        """
        Add fertilizer to the field.

        Adds 20 to the field's fertilizer percentage given the field is less than 80% fertilized.
        """

        # Users can only fertilize their field it is 80% fertilized or less
        if self.fertilizer_percent > 80:
            print("You cannot fertilize right now (too much fertilizer)!")
        else:
            self.fertilizer_percent += 20
            print(f"You added fertilzer to your field, its fertilizer percentage is now {self.fertilizer_percent}")
    
    def plant_crop(self, user_obj, plant_type):
        """
        Plant a crop in the field.

        Args:
            user_obj  (User): The User object that represents the current user
            plant_type (str): The type of crop to be planted.

        """

        # Users cannot plant crops if their field is full
        if self.num_plants == 100:
            print("Your field is full, harvest some crops before planting more!")
        else:
            self.num_plants = self.num_plants + 1
            plant_crop_db(user_obj, plant_type)
            print(f"You planted a {plant_type} crop in your field! There are now {self.num_plants} in your field.")

    def harvest_crop(self, crop_id):
        """
        Harvest a fully grown crop

        This method is unfinished, it will be updated as development progresses and when the SQL database is created.
        Currently, it just decrements the number of plants in the field if it isn't empty.

        Args:
            crop_id (int): The id of the crop to be harvested
        """

        # Users cannot harvest from an empty field
        if self.num_plants <= 0:
            print("There are no plants to harvest!")
        else:
            self.num_plants -= 1
            print(f"You harvested a crop with ID {crop_id}, there are now {self.num_plants} in your field.")
