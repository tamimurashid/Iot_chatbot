from db_config import *
from sms_handler import *
from email_handler import *
import re
def evaluate_condition(sensor_val_str, condition_str):
    """
    Evaluate a condition which can be numeric (e.g. '>30') or string (e.g. '==rain').
    """
    try:
        # Strip sensor value
        sensor_val_cleaned = sensor_val_str.strip().lower()

        # Determine if this is a string comparison
        if re.match(r'^(==|=)[a-zA-Z]+$', condition_str):
            expected = condition_str.split('=')[-1].strip().lower()
            return sensor_val_cleaned == expected

        # Extract operator and threshold for numeric comparison
        operator = condition_str[:1]
        if condition_str[1] in "=<>":  # for >=, <=
            operator += condition_str[1]
            threshold = float(condition_str[2:])
        else:
            threshold = float(condition_str[1:])

        # Extract numeric part of the sensor value
        sensor_val = ''.join([c for c in sensor_val_str if c.isdigit() or c == '.' or c == '-'])
        sensor_val = float(sensor_val)

        # Evaluate numeric condition
        if operator == ">" and sensor_val > threshold:
            return True
        elif operator == "<" and sensor_val < threshold:
            return True
        elif operator == ">=" and sensor_val >= threshold:
            return True
        elif operator == "<=" and sensor_val <= threshold:
            return True
        elif operator in ["==", "="] and sensor_val == threshold:
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
        username = user.get("username")
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
                full_message = f"Hello {username}\nCurrent {param} is {sensor_value}\n{message}"

                # Send alert(s)
                if alert_type in ["sms", "both"] and phone:
                    result = Send_sms(phone, full_message, user_id)
                    messages.append(f"SMS: {result}")

                if alert_type in ["email", "both"] and email:
                    result = send_email_notification(full_message, user_id)
                    messages.append(f"Email: {result.get_json().get('reply')}")

    return messages