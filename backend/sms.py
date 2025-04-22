import requests
import os

BEAM_AFRICA_API_KEY = os.getenv('BEAM_AFRICA_API_KEY')  # Load API key from environment variable
BEAM_AFRICA_ENDPOINT = 'https://apisms.beem.africa/v1/send'

def send_sms(msg):
    settings = get_user_settings(device_id)  # You can pass device_id as an argument
    phone = settings.get("phone_number", "")
    if not phone:
        return "⚠️ Please configure your phone number."
    payload = {
        "api_key": BEAM_AFRICA_API_KEY,
        "to": phone,
        "message": msg,
    }
    response = requests.post(BEAM_AFRICA_ENDPOINT, data=payload)
    return "✅ SMS sent!" if response.status_code == 200 else "❌ Failed to send SMS."

def configure_sms(phone_number):
    device_id = str(uuid.uuid4())  # Unique device ID
    save_user_settings(device_id, None, None, phone_number, None, None, None)
    return f"Phone number {phone_number} saved with device ID: {device_id}"
