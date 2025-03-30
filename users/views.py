import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from .models import User


def validate_object_id(value):
    """Check if the provided ID is a valid ObjectId"""
    return ObjectId.is_valid(value)


@method_decorator(csrf_exempt, name="dispatch")
class UserView(View):
    def post(self, request):
        """Create a new user or bulk create users"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        if isinstance(data, list):
            user_ids = User.bulk_create(data)
            new_users = [User.get_by_id(user_id) for user_id in user_ids]
            return JsonResponse(
                {"message": "Users created successfully", "data": new_users}, status=201
            )

        required_fields = ["username", "email", "password"]
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"message": "Missing required fields", "data": None}, status=400
            )

        user_id = User.create(**data)
        new_user = User.get_by_id(user_id)
        return JsonResponse(
            {"message": "User created successfully", "data": new_user},
            status=201,
        )

    def get(self, request):
        """Get all users"""
        users = User.get_all()
        return JsonResponse(
            {
                "message": "Users retrieved successfully",
                "data": users,
                "count": len(users),
            },
            status=200,
            safe=False,
        )


@method_decorator(csrf_exempt, name="dispatch")
class UserDetailView(View):
    def get(self, request, user_id):
        """Get a specific user by ID"""
        if not validate_object_id(user_id):
            return JsonResponse(
                {"message": "Invalid user ID format", "data": None}, status=400
            )

        user = User.get_by_id(user_id)
        if not user:
            return JsonResponse({"message": "User not found", "data": None}, status=404)
        return JsonResponse(
            {"message": "User retrieved successfully", "data": user},
            status=200,
        )

    def put(self, request, user_id):
        """Update an existing user"""
        if not validate_object_id(user_id):
            return JsonResponse(
                {"message": "Invalid user ID format", "data": None}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        success = User.update(user_id, data)
        if success:
            updated_user = User.get_by_id(user_id)
            return JsonResponse(
                {"message": "User updated successfully", "data": updated_user},
                status=200,
            )
        return JsonResponse({"message": "User not found", "data": None}, status=404)

    def delete(self, request, user_id):
        """Delete a user"""
        if not validate_object_id(user_id):
            return JsonResponse(
                {"message": "Invalid user ID format", "data": None}, status=400
            )

        success = User.delete(user_id)
        return JsonResponse(
            {
                "message": (
                    "User deleted successfully" if success else "Failed to delete user"
                )
            },
            status=200 if success else 500,
        )
