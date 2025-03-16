from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import RegisteredUser
from django.contrib.auth.hashers import make_password, check_password

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_user(request):
    print("register_user was called") 

    if request.method == "OPTIONS":
        print("Handling OPTIONS request")
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        print("Raw request body:", body_unicode)

        data = json.loads(body_unicode)
        print("Parsed JSON data:", data)

        required_fields = ["first_name", "last_name", "username", "email", "password"]
        if not all(key in data for key in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if RegisteredUser.objects.filter(email=data["email"]).exists():
            return JsonResponse({"error": "User already exists"}, status=400)

        hashed_pw = make_password(data["password"])
        new_user = RegisteredUser.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"],
            hashed_password=hashed_pw,
        )
        
        return JsonResponse({"message": f"User {new_user.username} successfully registered"}, status=201)

    except json.JSONDecodeError:
        print("JSON Decode Error")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_user(request):
    print("login_user was called")

    if request.method == "OPTIONS":
        print("Handling OPTIONS request")
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        print("Raw request body:", body_unicode)

        data = json.loads(body_unicode)
        print("Parsed JSON data:", data)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Missing email or password"}, status=400)

        user = RegisteredUser.objects.filter(email=email).first()
        print(f"User found: {user}") 

        if user and check_password(password, user.hashed_password):
            print(f"Login successful for: {user.first_name}")  
            return JsonResponse({"message": f"Welcome back, {user.first_name}!", "is_admin": user.is_admin }, status=200)

        print("Invalid credentials")
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    except json.JSONDecodeError:
        print("JSON Decode Error")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
@require_http_methods(["GET"])
def get_user_data(request):
    users = RegisteredUser.objects.all().values("first_name", "last_name", "email", "username")
    return JsonResponse(list(users), safe=False)
