import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from .models import Product, Category


def validate_object_id(value):
    """Validate if a string is a valid MongoDB ObjectId"""
    return ObjectId.is_valid(value)


@method_decorator(csrf_exempt, name="dispatch")
class ProductView(View):
    def post(self, request):
        """Create a new product or bulk create products"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

        # Handle bulk creation
        if isinstance(data, list):
            product_ids = Product.bulk_create(data)
            if not product_ids:
                return JsonResponse(
                    {"status": "error", "message": "Failed to create products"},
                    status=400,
                )

            products = [Product.get_by_id(pid) for pid in product_ids]
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Created {len(products)} products",
                    "data": products,
                },
                status=201,
            )

        # Handle single product creation
        required_fields = [
            "name",
            "description",
            "price",
            "quantity",
            "category_id",
            "supplier_id",
            "sku",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                },
                status=400,
            )

        if not validate_object_id(data["category_id"]) or not validate_object_id(
            data["supplier_id"]
        ):
            return JsonResponse(
                {"status": "error", "message": "Invalid category or supplier ID"},
                status=400,
            )

        product_id = Product.create(**data)
        product = Product.get_by_id(product_id)
        return JsonResponse(
            {
                "status": "success",
                "message": "Product created successfully",
                "data": product,
            },
            status=201,
        )

    def get(self, request):
        """Get all products"""
        products = Product.get_all()
        return JsonResponse(
            {
                "status": "success",
                "message": f"Found {len(products)} products",
                "data": products,
                "count": len(products),
            },
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductDetailView(View):
    def get(self, request, product_id):
        """Get a specific product"""
        if not validate_object_id(product_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid product ID format"}, status=400
            )

        product = Product.get_by_id(product_id)
        if not product:
            return JsonResponse(
                {"status": "error", "message": "Product not found"}, status=404
            )

        return JsonResponse(
            {
                "status": "success",
                "message": "Product retrieved successfully",
                "data": product,
            },
            status=200,
        )

    def put(self, request, product_id):
        """Update a product"""
        if not validate_object_id(product_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid product ID format"}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

        # Validate category_id if present
        if "category_id" in data and not validate_object_id(data["category_id"]):
            return JsonResponse(
                {"status": "error", "message": "Invalid category ID"}, status=400
            )

        # Validate supplier_id if present
        if "supplier_id" in data and not validate_object_id(data["supplier_id"]):
            return JsonResponse(
                {"status": "error", "message": "Invalid supplier ID"}, status=400
            )

        success = Product.update(product_id, data)
        if not success:
            return JsonResponse(
                {"status": "error", "message": "Product update failed"}, status=400
            )

        updated_product = Product.get_by_id(product_id)
        return JsonResponse(
            {
                "status": "success",
                "message": "Product updated successfully",
                "data": updated_product,
            },
            status=200,
        )

    def delete(self, request, product_id):
        """Delete a product"""
        if not validate_object_id(product_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid product ID format"}, status=400
            )

        success = Product.delete(product_id)
        if not success:
            return JsonResponse(
                {"status": "error", "message": "Product not found or already deleted"},
                status=404,
            )

        return JsonResponse(
            {"status": "success", "message": "Product deleted successfully"}, status=200
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductSearchView(View):
    def get(self, request):
        """Search products with filters"""
        query_params = request.GET
        criteria = {}

        # Price range filter
        if "min_price" in query_params or "max_price" in query_params:
            try:
                price_filter = {}
                if "min_price" in query_params:
                    price_filter["$gte"] = float(query_params["min_price"])
                if "max_price" in query_params:
                    price_filter["$lte"] = float(query_params["max_price"])
                criteria["price"] = price_filter
            except ValueError:
                return JsonResponse(
                    {"status": "error", "message": "Invalid price value"}, status=400
                )

        # Name search (partial match)
        if "name" in query_params:
            criteria["name"] = {"$regex": query_params["name"], "$options": "i"}

        # Category filter
        if "category_id" in query_params:
            if not validate_object_id(query_params["category_id"]):
                return JsonResponse(
                    {"status": "error", "message": "Invalid category ID"}, status=400
                )
            criteria["category_id"] = ObjectId(query_params["category_id"])

        # Quantity filter
        if "min_quantity" in query_params:
            try:
                criteria["quantity"] = {"$gte": int(query_params["min_quantity"])}
            except ValueError:
                return JsonResponse(
                    {"status": "error", "message": "Invalid quantity value"}, status=400
                )

        products = Product.get_by_criteria(criteria)
        return JsonResponse(
            {
                "status": "success",
                "message": f"Found {len(products)} matching products",
                "data": products,
                "count": len(products),
            },
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductMetricsView(View):
    def get(self, request):
        """Get product metrics"""
        metrics = Product.calculate_metrics()
        return JsonResponse(
            {
                "status": "success",
                "message": "Product metrics calculated",
                "data": metrics,
            },
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductSortView(View):
    def get(self, request):
        """Get sorted and paginated products"""
        query_params = request.GET

        # Validate sort field
        valid_sort_fields = ["name", "price", "quantity", "created_at"]
        sort_by = query_params.get("sort_by", "price")
        if sort_by not in valid_sort_fields:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Invalid sort field. Valid fields: {', '.join(valid_sort_fields)}",
                },
                status=400,
            )

        # Validate sort order
        try:
            order = int(query_params.get("order", 1))
            if order not in (1, -1):
                raise ValueError
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "Order must be 1 (asc) or -1 (desc)"},
                status=400,
            )

        # Validate pagination
        try:
            limit = int(query_params.get("limit", 10))
            skip = int(query_params.get("skip", 0))
            if limit < 1 or skip < 0:
                raise ValueError
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "Invalid pagination parameters"},
                status=400,
            )

        products = Product.get_sorted_products(sort_by, order, limit, skip)
        return JsonResponse(
            {
                "status": "success",
                "message": f"Retrieved {len(products)} products",
                "data": products,
                "count": len(products),
            },
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CategoryView(View):
    def post(self, request):
        """Create a new category or bulk create categories"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

        # Handle bulk creation
        if isinstance(data, list):
            category_ids = Category.bulk_create(data)
            if not category_ids:
                return JsonResponse(
                    {"status": "error", "message": "Failed to create categories"},
                    status=400,
                )

            categories = [Category.get_by_id(cid) for cid in category_ids]
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Created {len(categories)} categories",
                    "data": categories,
                },
                status=201,
            )

        # Handle single category creation
        required_fields = ["name"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                },
                status=400,
            )

        category_id = Category.create(
            name=data["name"], description=data.get("description")
        )
        category = Category.get_by_id(category_id)
        return JsonResponse(
            {
                "status": "success",
                "message": "Category created successfully",
                "data": category,
            },
            status=201,
        )

    def get(self, request):
        """Get all categories"""
        categories = Category.get_all()
        return JsonResponse(
            {
                "status": "success",
                "message": f"Found {len(categories)} categories",
                "data": categories,
                "count": len(categories),
            },
            status=200,
        )


@method_decorator(csrf_exempt, name="dispatch")
class CategoryDetailView(View):
    def get(self, request, category_id):
        """Get a specific category"""
        if not validate_object_id(category_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid category ID format"}, status=400
            )

        category = Category.get_by_id(category_id)
        if not category:
            return JsonResponse(
                {"status": "error", "message": "Category not found"}, status=404
            )

        return JsonResponse(
            {
                "status": "success",
                "message": "Category retrieved successfully",
                "data": category,
            },
            status=200,
        )

    def put(self, request, category_id):
        """Update a category"""
        if not validate_object_id(category_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid category ID format"}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

        if "name" in data and not data["name"]:
            return JsonResponse(
                {"status": "error", "message": "Category name cannot be empty"},
                status=400,
            )

        success = Category.update(category_id, data)
        if not success:
            return JsonResponse(
                {"status": "error", "message": "Category update failed"}, status=400
            )

        updated_category = Category.get_by_id(category_id)
        return JsonResponse(
            {
                "status": "success",
                "message": "Category updated successfully",
                "data": updated_category,
            },
            status=200,
        )

    def delete(self, request, category_id):
        """Delete a category"""
        if not validate_object_id(category_id):
            return JsonResponse(
                {"status": "error", "message": "Invalid category ID format"}, status=400
            )

        success = Category.delete(category_id)
        if not success:
            return JsonResponse(
                {"status": "error", "message": "Category not found or already deleted"},
                status=404,
            )

        return JsonResponse(
            {"status": "success", "message": "Category deleted successfully"},
            status=200,
        )
