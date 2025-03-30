import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from bson import ObjectId
from .models import Location


def validate_object_id(value):
    """Check if the provided ID is a valid ObjectId"""
    return ObjectId.is_valid(value)


@method_decorator(csrf_exempt, name="dispatch")
class LocationView(View):
    def post(self, request):
        """Create a new location or bulk create locations"""
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        if isinstance(data, list):
            location_ids = Location.bulk_create(data)
            new_locations = [
                Location.get_by_id(location_id) for location_id in location_ids
            ]
            return JsonResponse(
                {"message": "Locations created successfully", "data": new_locations},
                status=201,
            )

        required_fields = ["name", "address", "city", "state", "country", "postal_code"]
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"message": "Missing required fields", "data": None}, status=400
            )

        location_id = Location.create(**data)
        new_location = Location.get_by_id(location_id)
        return JsonResponse(
            {"message": "Location created successfully", "data": new_location},
            status=201,
        )

    def get(self, request):
        """Get all locations"""
        locations = Location.get_all()
        return JsonResponse(
            {
                "message": "Locations retrieved successfully",
                "data": locations,
                "count": len(locations),
            },
            status=200,
            safe=False,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LocationDetailView(View):
    def get(self, request, location_id):
        """Get a specific location by ID"""
        if not validate_object_id(location_id):
            return JsonResponse(
                {"message": "Invalid location ID format", "data": None}, status=400
            )

        location = Location.get_by_id(location_id)
        if not location:
            return JsonResponse(
                {"message": "Location not found", "data": None}, status=404
            )
        return JsonResponse(
            {"message": "Location retrieved successfully", "data": location},
            status=200,
        )

    def put(self, request, location_id):
        """Update an existing location"""
        if not validate_object_id(location_id):
            return JsonResponse(
                {"message": "Invalid location ID format", "data": None}, status=400
            )

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON format", "data": None}, status=400
            )

        success = Location.update(location_id, data)
        if success:
            updated_location = Location.get_by_id(location_id)
            return JsonResponse(
                {"message": "Location updated successfully", "data": updated_location},
                status=200,
            )
        return JsonResponse({"message": "Location not found", "data": None}, status=404)

    def delete(self, request, location_id):
        """Delete a location"""
        if not validate_object_id(location_id):
            return JsonResponse(
                {"message": "Invalid location ID format", "data": None}, status=400
            )

        success = Location.delete(location_id)
        return JsonResponse(
            {
                "message": (
                    "Location deleted successfully"
                    if success
                    else "Failed to delete location"
                )
            },
            status=200 if success else 500,
        )
