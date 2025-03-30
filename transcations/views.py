import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from .models import InventoryTransaction


def validate_object_id(value):
    """Check if the provided ID is a valid ObjectId"""
    return ObjectId.is_valid(value)


@method_decorator(csrf_exempt, name="dispatch")
class InventoryTransactionView(View):
    def post(self, request):
        """Create a new inventory transaction or bulk create transactions"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        if isinstance(data, list):
            transaction_ids = InventoryTransaction.bulk_create(data)
            new_transactions = [
                InventoryTransaction.get_by_id(transaction_id)
                for transaction_id in transaction_ids
            ]
            return JsonResponse(
                {
                    "message": "Transactions created successfully",
                    "data": new_transactions,
                },
                status=201,
            )

        required_fields = ["product_id", "quantity", "transaction_type"]
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"message": "Missing required fields", "data": None}, status=400
            )

        transaction_id = InventoryTransaction.create(**data)
        new_transaction = InventoryTransaction.get_by_id(transaction_id)
        return JsonResponse(
            {"message": "Transaction created successfully", "data": new_transaction},
            status=201,
        )

    def get(self, request):
        """Get all inventory transactions"""
        transactions = InventoryTransaction.get_all()
        return JsonResponse(
            {
                "message": "Transactions retrieved successfully",
                "data": transactions,
                "count": len(transactions),
            },
            status=200,
            safe=False,
        )


@method_decorator(csrf_exempt, name="dispatch")
class InventoryTransactionDetailView(View):
    def get(self, request, transaction_id):
        """Get a specific inventory transaction by ID"""
        if not validate_object_id(transaction_id):
            return JsonResponse(
                {"message": "Invalid transaction ID format", "data": None}, status=400
            )

        transaction = InventoryTransaction.get_by_id(transaction_id)
        if not transaction:
            return JsonResponse(
                {"message": "Transaction not found", "data": None}, status=404
            )
        return JsonResponse(
            {"message": "Transaction retrieved successfully", "data": transaction},
            status=200,
        )

    def put(self, request, transaction_id):
        """Update an existing inventory transaction"""
        if not validate_object_id(transaction_id):
            return JsonResponse(
                {"message": "Invalid transaction ID format", "data": None}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        success = InventoryTransaction.update(transaction_id, data)
        if success:
            updated_transaction = InventoryTransaction.get_by_id(transaction_id)
            return JsonResponse(
                {
                    "message": "Transaction updated successfully",
                    "data": updated_transaction,
                },
                status=200,
            )
        return JsonResponse(
            {"message": "Transaction not found", "data": None}, status=404
        )

    def delete(self, request, transaction_id):
        """Delete an inventory transaction"""
        if not validate_object_id(transaction_id):
            return JsonResponse(
                {"message": "Invalid transaction ID format", "data": None}, status=400
            )

        success = InventoryTransaction.delete(transaction_id)
        return JsonResponse(
            {
                "message": (
                    "Transaction deleted successfully"
                    if success
                    else "Failed to delete transaction"
                )
            },
            status=200 if success else 500,
        )
