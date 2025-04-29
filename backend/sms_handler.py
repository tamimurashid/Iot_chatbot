from conf import BEAM_AFRICA_API_KEY, BEAM_AFRICA_SECRET_KEY, url
from requests.auth import HTTPBasicAuth
import requests

url = "https://apisms.beem.africa/v1/send"


#Function to send SMS using Beam Africa API
def Send_sms(phone,  message):
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

    username = BEAM_AFRICA_API_KEY
    password = BEAM_AFRICA_SECRET_KEY

    try:
        response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            reply = f"SMS sent successfully to {phone}"
        else:
            reply = (
                f"Failed to send SMS.\n"
                f"Status code: {response.status_code}\n"
                f"Reason: {response.reason}\n"
                f"Details: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        reply = f"Request failed: {e}"

    return reply



