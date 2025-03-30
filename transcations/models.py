from bson import ObjectId
from datetime import datetime
from db_connection import db


class InventoryTransaction:
    collection = db["inventory_transactions"]

    @classmethod
    def create(cls, product_id, quantity, transaction_type, reference):
        """Create a new inventory transaction"""
        transaction_data = {
            "product_id": ObjectId(product_id),
            "quantity": int(quantity),
            "transaction_type": transaction_type,
            "reference": reference,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(transaction_data)
        return str(result.inserted_id)

    @classmethod
    def get_all(cls):
        """Get all inventory transactions with _id and product_id converted to string"""
        transactions = []
        for transaction in cls.collection.find():
            transaction["id"] = str(transaction["_id"])
            transaction["product_id"] = str(transaction["product_id"])
            del transaction["_id"]
            transactions.append(transaction)
        return transactions

    @classmethod
    def get_by_id(cls, transaction_id):
        """Get single inventory transaction by ID"""
        try:
            transaction = cls.collection.find_one({"_id": ObjectId(transaction_id)})
            if transaction:
                transaction["id"] = str(transaction["_id"])
                transaction["product_id"] = str(transaction["product_id"])
                del transaction["_id"]
                return transaction
            return None
        except:
            return None

    @classmethod
    def update(cls, transaction_id, update_data):
        """Update inventory transaction information"""
        if "product_id" in update_data:
            update_data["product_id"] = ObjectId(update_data["product_id"])
        update_data["updated_at"] = datetime.utcnow()
        result = cls.collection.update_one(
            {"_id": ObjectId(transaction_id)}, {"$set": update_data}
        )
        return result.modified_count > 0

    @classmethod
    def delete(cls, transaction_id):
        """Delete an inventory transaction"""
        result = cls.collection.delete_one({"_id": ObjectId(transaction_id)})
        return result.deleted_count > 0

    @classmethod
    def bulk_create(cls, transactions):
        """Bulk create inventory transactions"""
        for transaction in transactions:
            transaction["product_id"] = ObjectId(transaction["product_id"])
            transaction["created_at"] = datetime.utcnow()
            transaction["updated_at"] = datetime.utcnow()
        result = cls.collection.insert_many(transactions)
        return [str(inserted_id) for inserted_id in result.inserted_ids]
