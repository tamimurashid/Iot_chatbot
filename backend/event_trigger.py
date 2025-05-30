from db_config import *
from sms_handler import *
from email_handler import *
from datetime import datetime, timedelta
import re

def evaluate_condition(sensor_val_str, condition_str):
    try:
        sensor_val_cleaned = sensor_val_str.strip().lower()
        if re.match(r'^(==|=)[a-zA-Z]+$', condition_str):
            expected = condition_str.split('=')[-1].strip().lower()
            return sensor_val_cleaned == expected

        operator = condition_str[:1]
        if condition_str[1] in "=<>":
            operator += condition_str[1]
            threshold = float(condition_str[2:])
        else:
            threshold = float(condition_str[1:])

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

        stream_data = {ds['parameter']: ds['latest_value'] for ds in datastreams}

        for idx, event in enumerate(events):
            param = event.get("parameter")
            condition = event.get("condition")
            message = event.get("message", f"Alert! Condition met for {param}")
            alert_type = event.get("alert", "both")
            timer_seconds = int(event.get("timer", 600))  # default 600 seconds (10 min)

            sensor_value = stream_data.get(param)
            if not sensor_value:
                continue

            if evaluate_condition(sensor_value, condition):
                now = datetime.utcnow()
                last_alert_str = event.get("last_alert_time")
                send_alert = False

                if last_alert_str:
                    last_alert_time = datetime.strptime(last_alert_str, "%Y-%m-%d %H:%M:%S")
                    elapsed = (now - last_alert_time).total_seconds()
                    if elapsed >= timer_seconds:
                        send_alert = True
                else:
                    send_alert = True  # Never alerted before

                if send_alert:
                    full_message = f"Hello {username}\nCurrent {param} is {sensor_value}\n{message}"

                    if alert_type in ["sms", "both"] and phone:
                        result = Send_sms(phone, full_message, user_id)
                        messages.append(f"SMS: {result}")

                    if alert_type in ["email", "both"] and email:
                        result = send_email_notification(full_message, user_id)
                        messages.append(f"Email: {result.get_json().get('reply')}")

                    # Update last_alert_time in event
                    events[idx]["last_alert_time"] = now.strftime("%Y-%m-%d %H:%M:%S")

        # Save updated events to database
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"events": events}}
        )

    return messages
