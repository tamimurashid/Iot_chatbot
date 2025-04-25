import mysql.connector
from bcrypt import hashpw, gensalt
import uuid

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='iot_chatbot'
    )

def save_user_settings(device_id, email, password, phone_number, smtp_server, smtp_port, secret_key):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    cursor.execute("""
        INSERT INTO users (device_id, email, email_password, phone_number, smtp_server, smtp_port, secret_key)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (device_id, email, hashed_password, phone_number, smtp_server, smtp_port, secret_key))
    
    connection.commit()
    cursor.close()
    connection.close()

def get_user_settings(device_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE device_id = %s", (device_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result
