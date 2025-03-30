from bson import ObjectId
from datetime import datetime
from db_connection import db


class Supplier:
    collection = db["suppliers"]

    @classmethod
    def create(cls, name, contact_info, email, address, phone):
        """Create a new supplier"""
        supplier_data = {
            "name": name,
            "email": email,
            "address": address,
            "phone": phone,
            "contact_info": contact_info,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(supplier_data)
        return str(result.inserted_id)

    @classmethod
    def get_all(cls):
        """Get all suppliers with _id converted to string"""
        suppliers = []
        for supplier in cls.collection.find():
            supplier["id"] = str(supplier["_id"])
            del supplier["_id"]
            suppliers.append(supplier)
        return suppliers

    @classmethod
    def get_by_id(cls, supplier_id):
        """Get single supplier by ID"""
        try:
            supplier = cls.collection.find_one({"_id": ObjectId(supplier_id)})
            if supplier:
                supplier["id"] = str(supplier["_id"])
                del supplier["_id"]
                return supplier
            return None
        except:
            return None

    @classmethod
    def update(cls, supplier_id, update_data):
        """Update supplier information"""
        update_data["updated_at"] = datetime.utcnow()
        result = cls.collection.update_one(
            {"_id": ObjectId(supplier_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, supplier_id):
        """Delete a supplier"""
        result = cls.collection.delete_one({"_id": ObjectId(supplier_id)})
        return result.deleted_count > 0

    @classmethod
    def bulk_create(cls, suppliers):
        """Bulk create suppliers"""
        for supplier in suppliers:
            supplier["created_at"] = datetime.utcnow()
            supplier["updated_at"] = datetime.utcnow()
        result = cls.collection.insert_many(suppliers)
        return [str(inserted_id) for inserted_id in result.inserted_ids]
