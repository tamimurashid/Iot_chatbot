

import requests
from requests.auth import HTTPBasicAuth

url = "https://apisms.beem.africa/v1/send"

data = {
    "source_addr": "dreamTek",
    "encoding": 0,
    "message": "SMS Test from Python API",
    "recipients": [
        {
            "recipient_id": 1,
            "dest_addr": "255768857064"
        }
    ]
}

username = "b830832c3323841e"
password = "NDQ3OWJkOGM1ZGQwM2Q0YjYxNTBiZmMxNTBkMzFmODQ0YTlhZWZkODY2ZDEwOTk1NTYyZWIwMDE0MTg4Y2RhMA=="

response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

if response.status_code == 200:
    print("SMS sent successfully!")
else:
    print("SMS sending failed. Status code:", response.status_code)
    print("Response:", response.text)

