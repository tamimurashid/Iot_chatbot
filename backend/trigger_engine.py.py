# === FILE: trigger_engine.py ===
import re
from backend.db_config import get_events, get_latest_iot_data, mark_event_notified
from sms_handler import send_sms
from email_handler import send_email_notification


def evaluate_condition(condition_str, sensor_value):
    try:
        condition = re.sub(r'[^0-9<>=.!]', '', condition_str)
        return eval(f"{sensor_value}{condition}")
    except:
        return False

def evaluate_events():
    events = get_events()
    data = get_latest_iot_data()
    pin_data = {entry["virtualPin"]: entry["value"] for entry in data}

    for event in events:
        vpin = event.get("virtualPin")
        condition = event.get("condition")
        message = event.get("message")
        alert_type = event.get("alert")
        user_id = event.get("user_id", "default_user")
        notified = event.get("notified", False)

        if notified:
            continue  # Skip already notified events

        if vpin in pin_data and evaluate_condition(condition, float(pin_data[vpin])):
            if alert_type in ["sms", "both"]:
                phone = get_user(user_id).get("phone")
                send_sms(phone, message, user_id)

            if alert_type in ["email", "both"]:
                send_email_notification(message, user_id)

            mark_event_notified(event["_id"])
