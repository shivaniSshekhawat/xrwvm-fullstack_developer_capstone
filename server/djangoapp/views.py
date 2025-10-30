from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


# Logger setup
logger = logging.getLogger(__name__)


# -----------------------------
#   Car API
# -----------------------------
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related("car_make")
    cars = [
        {"CarModel": car_model.name, "CarMake": car_model.car_make.name}
        for car_model in car_models
    ]
    return JsonResponse({"CarModels": cars})


# -----------------------------
#   Authentication APIs
# -----------------------------
@csrf_exempt
def login_user(request):
    """Handle user login. Expects JSON body with `userName` and `password`."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse(
                    {"userName": username, "status": "Authenticated"}
                )
            return JsonResponse(
                {"userName": username, "status": "Failed"},
                status=401,
            )
        except Exception as e:
            logger.error(f"Login error: {e}")
            return JsonResponse(
                {"status": "Error", "message": str(e)},
                status=500,
            )

    return JsonResponse({"status": "Method Not Allowed"}, status=405)


@csrf_exempt
def logout_user(request):
    """Handle user logout."""
    if request.method == "POST":
        logout(request)
        return JsonResponse({"userName": ""})
    return JsonResponse({"status": "Method Not Allowed"}, status=405)


@csrf_exempt
def register(request):
    """Handle user registration."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("userName")
            password = data.get("password")
            first_name = data.get("firstName")
            last_name = data.get("lastName")
            email = data.get("email")

            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {
                        "userName": username,
                        "error": "Username already registered",
                    },
                    status=400,
                )

            if User.objects.filter(email=email).exists():
                return JsonResponse(
                    {
                        "email": email,
                        "error": "Email already registered",
                    },
                    status=400,
                )

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            login(request, user)
            return JsonResponse(
                {"userName": username, "status": "Authenticated"},
                status=201,
            )
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return JsonResponse(
                {"status": "Error", "message": str(e)},
                status=500,
            )

    return JsonResponse({"status": "Method Not Allowed"}, status=405)


# -----------------------------
#   Dealer APIs
# -----------------------------
def get_dealerships(request, state="All"):
    """Fetch all dealers or filter by state."""
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """Fetch a single dealer by ID."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """Fetch dealer reviews and analyze sentiment."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail["review"])
            review_detail["sentiment"] = response["sentiment"]
        return JsonResponse({"status": 200, "reviews": reviews})
    return JsonResponse({"status": 400, "message": "Bad Request"})


@csrf_exempt
def add_review(request):
    """Add a review if the user is authenticated."""
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            print(response)
            return JsonResponse(
                {"status": 200, "message": "Review posted successfully"}
            )
        except Exception as e:
            print(f"Error posting review: {e}")
            return JsonResponse(
                {"status": 401, "message": "Error in posting review"}
            )
    return JsonResponse({"status": 403, "message": "Unauthorized"})
