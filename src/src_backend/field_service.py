from datetime import datetime, timezone

import config
from database import water_field_db, fertilize_field_db, plant_crop_db, harvest_crop_db, get_field_data, get_planted_crops, remove_item_inventory_db, add_item_inventory_db

def get_predicted_field_status(user_id):
    field_data = get_field_data(user_id)

    if not field_data:
        return {
            "exists": False,
            "user_id": user_id,
            "field_id": None,
            "num_planted": 0,
            "moisture_percent": 0,
            "fertilizer_percent": 0,
            "crops": [],
        }

    field_id = field_data['field_id']
    crops = get_planted_crops(user_id)

    moisture_percent = field_data["moisture_percent"]
    fertilizer_percent = field_data["fertilizer_percent"]
    date_until_no_growth = field_data["date_until_no_growth"]
    last_updated = field_data["last_updated"]

    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - last_updated).total_seconds()

    if now <= date_until_no_growth:
        effective_seconds_of_growth = (now - last_updated).total_seconds()
    else:
        effective_seconds_of_growth = (date_until_no_growth - last_updated).total_seconds()

    predicted_moisture_now = max(0, moisture_percent - (config.MOISTURE_DECAY_RATE * elapsed_seconds))
    predicted_fertilizer_now = max(0, fertilizer_percent - (config.FERTILIZER_DECAY_RATE * elapsed_seconds))

    crop_info = []
    for crop in crops:
        time_grown = crop['total_time_grown'] + effective_seconds_of_growth
        ready_to_harvest = time_grown >= crop['total_growth_time_seconds']

        crop_info.append({
            "planted_crop_id": crop["planted_crop_id"],
            "crop_type": crop["crop_type"],
            "ready_to_harvest": ready_to_harvest,
            "time_grown": time_grown,
            "time_until_grown": max(0, crop["total_growth_time_seconds"] - time_grown),
        })

    return {
        "exists": True,
        "user_id": user_id,
        "field_id": field_id,
        "num_planted": field_data["num_planted"],
        "moisture_percent": predicted_moisture_now,
        "fertilizer_percent": predicted_fertilizer_now,
        "crops": crop_info,
    }

def get_field(user_id):
    """
    Service method to get the user's field data

    Args:
        user_id (int): The id of the current user

    """
    predicted_field_data = get_predicted_field_status(user_id)

    if not predicted_field_data["exists"]:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_NOT_FOUND",
                "message": "This user does not have a field!"
            }
        }
    else:
        return {
            "ok": True,
            "data": {
                "field": predicted_field_data
            }
        }


def water_field(user_id):
    """
    Water the user's field

    Args:
        user_id (int): The id of the current user

    """
    predicted_field_data = get_predicted_field_status(user_id)
    moisture_percent = predicted_field_data['moisture_percent']


    if moisture_percent > 90:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_FULLY_WATERED",
                "message": "Your field is already fully watered!"
            },
        }
    else:
        water_field_db(user_id)
        return {
            "ok": True,
            "data": {
                "field": get_predicted_field_status(user_id)
            },
        }

def fertilize_field(user_id):
    """
    Fertilize the user's field

    Args:
        user_id (int): The id of the current user

    """
    predicted_field_data = get_predicted_field_status(user_id)

    if not predicted_field_data["exists"]:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_NOT_FOUND",
                "message": "This user does not have a field!"
            }
        }

    fertilizer_percent = predicted_field_data['fertilizer_percent']

    if fertilizer_percent > 80:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_FULLY_FERTILIZED",
                "message": "Your field is already fully fertilized!"
            },
        }
    else:
        fertilize_field_db(user_id)
        return {
            "ok": True,
            "data": {
                "field": get_predicted_field_status(user_id)
            },
        }

def plant_crop(user_id, crop_type):
    """
    Plant a crop in the user's field

    Args:
        user_id (int): The id of the current user
        crop_type (str): The type of crop to plant

    """
    predicted_field_data = get_predicted_field_status(user_id)

    if not predicted_field_data["exists"]:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_NOT_FOUND",
                "message": "This user does not have a field!"
            }
        }

    plant_crop_result = plant_crop_db(user_id, crop_type)

    if not plant_crop_result["ok"]:
        return {
            "ok": False,
            "error": {
                "code": plant_crop_result["error"]["code"],
                "message": plant_crop_result["error"]["message"]
            }
        }

    remove_seed_result = remove_item_inventory_db(user_id, crop_type + " Seed")

    if not remove_seed_result["ok"]:
        return {
            "ok": False,
            "error": {
                "code": remove_seed_result["error"]["code"],
                "message": remove_seed_result["error"]["message"]
            }
        }

    return {
        "ok": True,
        "data": {
            "field": get_predicted_field_status(user_id)
        }
    }

def harvest_crop(user_id, planted_crop_id):
    """
    Harvest a crop from the user's field

    Args:
        user_id (int): The id of the current user
        planted_crop_id (int): The id of the crop to harvest

    """

    predicted_field_data = get_predicted_field_status(user_id)

    if not predicted_field_data["exists"]:
        return {
            "ok": False,
            "error": {
                "code": "FIELD_NOT_FOUND",
                "message": "This user does not have a field!"
            }
        }

    crops = predicted_field_data['crops']

    for crop in crops:
        if crop['planted_crop_id'] == planted_crop_id:
            if not crop['ready_to_harvest']:
                return {
                    "ok": False,
                    "error": {
                        "code": "CROP_NOT_READY",
                        "message": f"The {crop['crop_type']} crop is not ready to harvest yet!"
                    }
                }
            else:
                harvest_crop_db(user_id, planted_crop_id)
                add_item_inventory_db(user_id, crop['crop_type'])
                add_item_inventory_db(user_id, crop['crop_type'] + ' Seed')
                return {
                    "ok": True,
                    "data": {
                        "field": get_predicted_field_status(user_id)
                    }
                }

    return {
        "ok": False,
        "error": {
            "code": "CROP_NOT_FOUND",
            "message": f"No crop with id {planted_crop_id} was found in your field!"
        }
    }