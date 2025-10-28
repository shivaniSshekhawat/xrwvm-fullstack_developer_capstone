from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import logging
import json

from .models import CarMake, CarModel
from .populate import initiate 

# Logger setup
logger = logging.getLogger(__name__)

# -----------------------------
#   Car API
# -----------------------------
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})


# -----------------------------
#   Authentication APIs
# -----------------------------

@csrf_exempt
def login_user(request):
    """
    Handle user login.
    Expects JSON body with `userName` and `password`.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
            else:
                return JsonResponse({"userName": username, "status": "Failed"}, status=401)
        except Exception as e:
            logger.error(f"Login error: {e}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    return JsonResponse({"status": "Method Not Allowed"}, status=405)


@csrf_exempt
def logout_user(request):
    """
    Handle user logout.
    """
    if request.method == "POST":
        logout(request)
        return JsonResponse({"userName": ""})
    return JsonResponse({"status": "Method Not Allowed"}, status=405)


@csrf_exempt
def register(request):
    """
    Handle user registration.
    Expects JSON body with userName, password, firstName, lastName, and email.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            email = data.get("email")

            if User.objects.filter(username=username).exists():
                return JsonResponse({"userName": username, "error": "Username already registered"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"email": email, "error": "Email already registered"}, status=400)

            # Create and log in new user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"}, status=201)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=500)
    return JsonResponse({"status": "Method Not Allowed"}, status=405)
