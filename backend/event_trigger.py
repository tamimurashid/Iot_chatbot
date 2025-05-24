from db_config import *
from sms_handler import *
from email_handler import *
import re
def evaluate_condition(sensor_val_str, condition_str):
    """Parse and evaluate string-based conditions like '>30'."""
    try:
        # Extract operator and value
        operator = condition_str[:1]
        if condition_str[1] in "=<>":  # support >=, <=
            operator += condition_str[1]
            threshold = float(condition_str[2:])
        else:
            threshold = float(condition_str[1:])

        # Remove units like ' C', '%', etc. if any
        sensor_val = ''.join([c for c in sensor_val_str if c.isdigit() or c == '.' or c == '-'])
        sensor_val = float(sensor_val)

        if operator == ">" and sensor_val > threshold:
            return True
        elif operator == "<" and sensor_val < threshold:
            return True
        elif operator == ">=" and sensor_val >= threshold:
            return True
        elif operator == "<=" and sensor_val <= threshold:
            return True
        elif operator == "==" and sensor_val == threshold:
            return True
        elif operator == "=" and sensor_val == threshold:
            return True
        else:
            return False
    except Exception as e:
        print(f"[Condition Error] {e}")
        return False


def check_and_alert():
    messages = []
    users = users_collection.find()

    for user in users:
        user_id = user.get("user_id", "default_user")
        phone = user.get("phone_number")
        email = user.get("email")
        events = user.get("events", [])
        datastreams = user.get("datastreams", [])

        if not events or not datastreams:
            continue

        # Create lookup dict from datastreams
        stream_data = {ds['parameter']: ds['latest_value'] for ds in datastreams}

        for event in events:
            param = event.get("parameter")
            condition = event.get("condition")  # e.g. '>30'
            message = event.get("message", f"Alert! Condition met for {param}")
            alert_type = event.get("alert", "both")

            sensor_value = stream_data.get(param)
            if not sensor_value:
                continue

            if evaluate_condition(sensor_value, condition):
                full_message = f"{param.upper()} = {sensor_value}, condition: {condition}\n{message}"

                # Send alert(s)
                if alert_type in ["sms", "both"] and phone:
                    result = Send_sms(phone, full_message, user_id)
                    messages.append(f"SMS: {result}")

                if alert_type in ["email", "both"] and email:
                    result = send_email_notification(full_message, user_id)
                    messages.append(f"Email: {result.get_json().get('reply')}")

    return messages