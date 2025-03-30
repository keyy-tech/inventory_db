from bson import ObjectId
from datetime import datetime
from db_connection import db


class Category:
    collection = db["categories"]

    @classmethod
    def create(cls, name, description=None):
        """Create a new category"""
        category_data = {
            "name": name,
            "description": description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(category_data)
        return str(result.inserted_id)

    @classmethod
    def get_by_id(cls, category_id):
        """Get a single category by ID"""
        try:
            if not ObjectId.is_valid(category_id):
                return None

            category = cls.collection.find_one({"_id": ObjectId(category_id)})
            if category:
                category["id"] = str(category["_id"])
                del category["_id"]
                return category
            return None
        except Exception:
            return None

    @classmethod
    def get_all(cls):
        """Get all categories"""
        categories = []
        for category in cls.collection.find():
            category["id"] = str(category["_id"])
            del category["_id"]
            categories.append(category)
        return categories

    @classmethod
    def update(cls, category_id, update_data):
        """Update a category"""
        try:
            if not ObjectId.is_valid(category_id):
                return False

            update_data["updated_at"] = datetime.utcnow()
            result = cls.collection.update_one(
                {"_id": ObjectId(category_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    @classmethod
    def delete(cls, category_id):
        """Delete a category"""
        try:
            if not ObjectId.is_valid(category_id):
                return False

            result = cls.collection.delete_one({"_id": ObjectId(category_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @classmethod
    def bulk_create(cls, categories):
        """Bulk create categories"""
        try:
            for category in categories:
                category["created_at"] = datetime.utcnow()
                category["updated_at"] = datetime.utcnow()

            result = cls.collection.insert_many(categories)
            return [str(id) for id in result.inserted_ids]
        except Exception:
            return []


class Product:
    collection = db["products"]

    @classmethod
    def create(cls, name, description, price, quantity, category_id, supplier_id, sku):
        """Create a new product"""
        product_data = {
            "name": name,
            "description": description,
            "price": float(price),
            "quantity": int(quantity),
            "category_id": ObjectId(category_id),
            "supplier_id": ObjectId(supplier_id),
            "sku": sku,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = cls.collection.insert_one(product_data)
        return str(result.inserted_id)

    @classmethod
    def get_by_id(cls, product_id):
        """Get a single product by ID"""
        try:
            if not ObjectId.is_valid(product_id):
                return None

            product = cls.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                product["id"] = str(product["_id"])
                product["category_id"] = str(product["category_id"])
                product["supplier_id"] = str(product["supplier_id"])
                del product["_id"]
                return product
            return None
        except Exception:
            return None

    @classmethod
    def get_all(cls):
        """Get all products with category details"""
        products = []
        for product in cls.collection.find():
            product["id"] = str(product["_id"])
            product["category_id"] = str(product["category_id"])
            product["supplier_id"] = str(product.get("supplier_id", ""))
            del product["_id"]

            # Add category details
            category = Category.get_by_id(product["category_id"])
            if category:
                product["category"] = category

            products.append(product)
        return products

    @classmethod
    def update(cls, product_id, update_data):
        """Update a product"""
        try:
            if not ObjectId.is_valid(product_id):
                return False

            if "category_id" in update_data:
                update_data["category_id"] = ObjectId(update_data["category_id"])
            if "supplier_id" in update_data:
                update_data["supplier_id"] = ObjectId(update_data["supplier_id"])

            update_data["updated_at"] = datetime.utcnow()
            result = cls.collection.update_one(
                {"_id": ObjectId(product_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False

    @classmethod
    def delete(cls, product_id):
        """Delete a product"""
        try:
            if not ObjectId.is_valid(product_id):
                return False

            result = cls.collection.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @classmethod
    def bulk_create(cls, products):
        """Bulk create products"""
        try:
            for product in products:
                product["category_id"] = ObjectId(product["category_id"])
                product["supplier_id"] = ObjectId(product["supplier_id"])
                product["created_at"] = datetime.utcnow()
                product["updated_at"] = datetime.utcnow()

            result = cls.collection.insert_many(products)
            return [str(id) for id in result.inserted_ids]
        except Exception:
            return []

    @classmethod
    def get_by_criteria(cls, criteria):
        """Get products by search criteria"""
        try:
            # Convert string IDs to ObjectIds if present
            if "category_id" in criteria:
                criteria["category_id"] = ObjectId(criteria["category_id"])
            if "supplier_id" in criteria:
                criteria["supplier_id"] = ObjectId(criteria["supplier_id"])

            products = []
            for product in cls.collection.find(criteria):
                product["id"] = str(product["_id"])
                product["category_id"] = str(product["category_id"])
                product["supplier_id"] = str(product["supplier_id"])
                del product["_id"]
                products.append(product)
            return products
        except Exception:
            return []

    @classmethod
    def calculate_metrics(cls):
        """Calculate product metrics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_products": {"$sum": 1},
                        "total_quantity": {"$sum": "$quantity"},
                        "average_price": {"$avg": "$price"},
                        "min_price": {"$min": "$price"},
                        "max_price": {"$max": "$price"},
                    }
                }
            ]
            result = list(cls.collection.aggregate(pipeline))
            return result[0] if result else {}
        except Exception:
            return {}

    @classmethod
    def get_sorted_products(cls, sort_by="price", order=1, limit=10, skip=0):
        """Get sorted products with pagination"""
        try:
            products = []
            cursor = cls.collection.find().sort(sort_by, order).skip(skip).limit(limit)
            for product in cursor:
                product["id"] = str(product["_id"])
                product["category_id"] = str(product["category_id"])
                product["supplier_id"] = str(product["supplier_id"])
                del product["_id"]
                products.append(product)
            return products
        except Exception:
            return []
