from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import logging
import json
# from .populate import initiate

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

@csrf_exempt
def login_user(request):
    """
    Handle user login.
    Expects JSON body with `userName` and `password`.
    Returns JSON with username and authentication status.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")

            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                # Successful login
                login(request, user)
                response_data = {"userName": username, "status": "Authenticated"}
            else:
                # Invalid credentials
                response_data = {"userName": username, "status": "Failed"}
        except Exception as e:
            logger.error(f"Login error: {e}")
            response_data = {"status": "Error", "message": str(e)}

        return JsonResponse(response_data)
    else:
        return JsonResponse({"status": "Method Not Allowed"}, status=405)

      
def logout_user(request):
    """
    Handle user logout.
    Terminates the current user session and returns an empty username.
    """
    if request.method == "POST":
        # Terminate the user session
        logout(request)
        # Return JSON with empty username
        data = {"userName": ""}
        return JsonResponse(data)
    else:
        return JsonResponse({"status": "Method Not Allowed"}, status=405)
          
@csrf_exempt

def register(request):
    """
    Handle user registration.
    Expects JSON body with:
        - userName
        - password
        - firstName
        - lastName
        - email

    Creates a new user, logs them in, and returns a JSON object with the username.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            email = data.get("email")

            # Check if the username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"userName": username, "error": "Username already registered"}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"email": email, "error": "Email already registered"}, status=400)

            # Create and save new user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            # Log the user in
            login(request, user)

            # Return success response
            return JsonResponse({"userName": username, "status": "Authenticated"}, status=201)

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=500)

    # Method not allowed
    return JsonResponse({"status": "Method Not Allowed"}, status=405)

