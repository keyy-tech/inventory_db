from bson import ObjectId
from datetime import datetime
from db_connection import db


class User:
    collection = db["users"]

    @classmethod
    def create(cls, username, email, password, first_name=None, last_name=None):
        """Create a new user"""
        user_data = {
            "username": username,
            "email": email,
            "password": password,  # Note: In a real application, ensure to hash the password
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(user_data)
        return str(result.inserted_id)

    @classmethod
    def get_all(cls):
        """Get all users with _id converted to string"""
        users = []
        for user in cls.collection.find():
            user["id"] = str(user["_id"])
            del user["_id"]
            users.append(user)
        return users

    @classmethod
    def get_by_id(cls, user_id):
        """Get single user by ID"""
        try:
            user = cls.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
                return user
            return None
        except:
            return None

    @classmethod
    def update(cls, user_id, update_data):
        """Update user information"""
        update_data["updated_at"] = datetime.utcnow()
        result = cls.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, user_id):
        """Delete a user"""
        result = cls.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @classmethod
    def bulk_create(cls, users):
        """Bulk create users"""
        for user in users:
            user["created_at"] = datetime.utcnow()
            user["updated_at"] = datetime.utcnow()
        result = cls.collection.insert_many(users)
        return [str(inserted_id) for inserted_id in result.inserted_ids]
