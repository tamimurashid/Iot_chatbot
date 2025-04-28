from config import BEAM_AFRICA_API_KEY, BEAM_AFRICA_SECRET_KEY
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

    response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        reply = message
    else:
        reply = "Failed to send SMS. please check your configuraation"
    
    return reply
    


