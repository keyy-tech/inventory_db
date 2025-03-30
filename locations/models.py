from bson import ObjectId
from datetime import datetime
from db_connection import db


class Location:
    collection = db["locations"]

    @classmethod
    def create(cls, name, address, city, state, country, postal_code):
        """Create a new location"""
        location_data = {
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "country": country,
            "postal_code": postal_code,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(location_data)
        return str(result.inserted_id)

    @classmethod
    def get_all(cls):
        """Get all locations with _id converted to string"""
        locations = []
        for location in cls.collection.find():
            location["id"] = str(location["_id"])
            del location["_id"]
            locations.append(location)
        return locations

    @classmethod
    def get_by_id(cls, location_id):
        """Get single location by ID"""
        try:
            location = cls.collection.find_one({"_id": ObjectId(location_id)})
            if location:
                location["id"] = str(location["_id"])
                del location["_id"]
                return location
            return None
        except:
            return None

    @classmethod
    def update(cls, location_id, update_data):
        """Update location information"""
        update_data["updated_at"] = datetime.utcnow()
        result = cls.collection.update_one(
            {"_id": ObjectId(location_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, location_id):
        """Delete a location"""
        result = cls.collection.delete_one({"_id": ObjectId(location_id)})
        return result.deleted_count > 0

    @classmethod
    def bulk_create(cls, locations):
        """Bulk create locations"""
        for location in locations:
            location["created_at"] = datetime.utcnow()
            location["updated_at"] = datetime.utcnow()
        result = cls.collection.insert_many(locations)
        return [str(inserted_id) for inserted_id in result.inserted_ids]
