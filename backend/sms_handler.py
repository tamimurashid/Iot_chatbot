from requests.auth import HTTPBasicAuth
import requests
from db_config import *

url = "https://apisms.beem.africa/v1/send"

def Send_sms(phone, message, user_id="default_user"):
    user_data = get_user(user_id)
    
    if not user_data:
        return "User not found."

    api_key = user_data.get("api_key")
    secret_key = user_data.get("secret_key")

    if not api_key or not secret_key:
        return "Missing Beam Africa API key or secret key."

    data = {
        "source_addr": "dreamTek",
        "encoding": 0,
        "message": message,
        "recipients": [
            {
                "recipient_id": 1,
                "dest_addr": phone
            }
        ]
    }

    try:
        response = requests.post(
            url,
            json=data,
            auth=HTTPBasicAuth(api_key, secret_key)
        )

        if response.status_code == 200:
            return f"SMS sent successfully to {phone}"
        else:
            return (
                f"Failed to send SMS.\n"
                f"Status code: {response.status_code}\n"
                f"Reason: {response.reason}\n"
                f"Details: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
