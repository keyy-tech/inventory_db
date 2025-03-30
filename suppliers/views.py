import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from .models import Supplier


def validate_object_id(value):
    """Check if the provided ID is a valid ObjectId"""
    return ObjectId.is_valid(value)


@method_decorator(csrf_exempt, name="dispatch")
class SupplierView(View):
    def post(self, request):
        """Create a new supplier or bulk create suppliers"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        if isinstance(data, list):
            supplier_ids = Supplier.bulk_create(data)
            new_suppliers = [
                Supplier.get_by_id(supplier_id) for supplier_id in supplier_ids
            ]
            return JsonResponse(
                {"message": "Suppliers created successfully", "data": new_suppliers},
                status=201,
            )

        required_fields = ["name", "contact_info", "email", "phone"]
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"message": "Missing required fields", "data": None}, status=400
            )

        supplier_id = Supplier.create(**data)
        new_supplier = Supplier.get_by_id(supplier_id)
        return JsonResponse(
            {"message": "Supplier created successfully", "data": new_supplier},
            status=201,
        )

    def get(self, request):
        """Get all suppliers"""
        suppliers = Supplier.get_all()
        return JsonResponse(
            {
                "message": "Suppliers retrieved successfully",
                "data": suppliers,
                "count": len(suppliers),
            },
            status=200,
            safe=False,
        )


@method_decorator(csrf_exempt, name="dispatch")
class SupplierDetailView(View):
    def get(self, request, supplier_id):
        """Get a specific supplier by ID"""
        if not validate_object_id(supplier_id):
            return JsonResponse(
                {"message": "Invalid supplier ID format", "data": None}, status=400
            )

        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            return JsonResponse(
                {"message": "Supplier not found", "data": None}, status=404
            )
        return JsonResponse(
            {"message": "Supplier retrieved successfully", "data": supplier}, status=200
        )

    def put(self, request, supplier_id):
        """Update an existing supplier"""
        if not validate_object_id(supplier_id):
            return JsonResponse(
                {"message": "Invalid supplier ID format", "data": None}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        success = Supplier.update(supplier_id, data)
        if success:
            updated_supplier = Supplier.get_by_id(supplier_id)
            return JsonResponse(
                {"message": "Supplier updated successfully", "data": updated_supplier},
                status=200,
            )
        return JsonResponse({"message": "Supplier not found", "data": None}, status=404)

    def delete(self, request, supplier_id):
        """Delete a supplier"""
        if not validate_object_id(supplier_id):
            return JsonResponse(
                {"message": "Invalid supplier ID format", "data": None}, status=400
            )

        success = Supplier.delete(supplier_id)
        return JsonResponse(
            {
                "message": (
                    "Supplier deleted successfully"
                    if success
                    else "Failed to delete supplier"
                )
            },
            status=200 if success else 500,
        )
