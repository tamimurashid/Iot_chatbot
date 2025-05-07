from pymongo import  MongoClient

client = MongoClient("mongodb://localhost:27017")

#select database and collection 
db = client["chatbot_db"]
users_collection =db["users"]



def get_or_create_user(user_id="default_user"):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        return user
    else:
        # Create user if not found
        new_user = {"user_id": user_id}
        users_collection.insert_one(new_user)
        return new_user
    

def update_user(user_id, new_data):
    """
    Updates user data if user exists, or creates a new user with the data.
    
    Args:
        user_id (str): The unique identifier of the user.
        new_data (dict): The new fields to update or insert.
    
    Returns:
        dict: The updated or newly created user document.
    """
    users_collection.update_one(
        {"user_id": user_id},       # filter by user_id
        {"$set": new_data},         # update the data
        upsert=True                 # insert if user doesn't exist
    )
    return users_collection.find_one({"user_id": user_id})

def get_user(user_id):
    return users_collection.find_one({"user_id": user_id})