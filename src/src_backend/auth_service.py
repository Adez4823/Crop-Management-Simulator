from database import insert_user_to_db, user_sign_in

from database import insert_user_to_db, user_sign_in, insert_new_user_field, load_user_field

DEFAULT_STARTING_MONEY = 100

def register_user(username: str, password: str):
    """
    Registers a new user in the system.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    Returns:
        dict: A dictionary containing the result.
    """
    username = username.strip()
    password = password.strip()

    if not username:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_USERNAME",
                "message": "Username cannot be empty."
            }
        }

    if not password:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_PASSWORD",
                "message": "Password cannot be empty."
            }
        }

    user_id = insert_user_to_db(username, password, DEFAULT_STARTING_MONEY)

    if user_id is None:
        return {
            "ok": False,
            "error": {
                "code": "USERNAME_TAKEN",
                "message": "Username already exists."
            }
        }


    insert_new_user_field(user_id)
    field_id, num_planted, moisture_percent, fertilizer_percent = load_user_field(user_id)

    return {
        "ok": True,
        "data": {
            "user": {
                "user_id": user_id,
                "username": username,
                "money": DEFAULT_STARTING_MONEY
            },
            "field": {
                "field_id": field_id,
                "num_planted": num_planted,
                "moisture_percent": moisture_percent,
                "fertilizer_percent": fertilizer_percent
            }
        }
    }


def user_login(username: str, password: str):
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_LOGIN_INPUT",
                "message": "Username and password are required."
            }
        }

    login_result = user_sign_in(username, password)

    if login_result is None:
        return {
            "ok": False,
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Incorrect username or password."
            }
        }

    money, user_id = login_result
    field_id, num_planted, moisture_percent, fertilizer_percent = load_user_field(user_id)

    return {
        "ok": True,
        "data": {
            "user": {
                "user_id": user_id,
                "username": username,
                "money": money
            },
            "field": {
                "field_id": field_id,
                "num_planted": num_planted,
                "moisture_percent": moisture_percent,
                "fertilizer_percent": fertilizer_percent
            }
        }
    }
    