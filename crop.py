class Crop:
    """
    Represents a crop that has been planted in a field.

    Contains info about that crop, its type and how long until it is fully grown.

    Attributes:
        plant_type (str): The type of plant that has been planted.
        moisture_percent (int): Time in seconds remaining until a crop is fully grown.

    """
        
    def __init__(self, plant_type, grow_time_remaining):
        self.plant_type = plant_type
        self.grow_time_remaining = grow_time_remaining