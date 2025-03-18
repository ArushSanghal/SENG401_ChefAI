from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import RegisteredUser, DietaryRestriction, SkillLevelChoices, Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from datetime import timedelta
from django.utils import timezone

class User:
    def __init__(self, skill_level=None, available_time=None):
        self.skill_level = skill_level
        self.available_time = available_time

class Guest(User):
    def __init__(self, skill_level=None, available_time=None):
        super().__init__(skill_level, available_time)

    def sign_up(self, data):
        required_fields = ["first_name", "last_name", "username", "email", "password"]
        if not all(key in data for key in required_fields):
            return {"error": "Missing required fields"}, 400

        if len(data["password"]) < 8:
            return {"error": "Password must be at least 8 characters long."}, 400

        if RegisteredUser.objects.filter(username=data["username"]).exists():
            return {"error": "Username already exists. Please choose another one."}, 400

        if RegisteredUser.objects.filter(email=data["email"]).exists():
            return {"error": "User with this email already exists."}, 400

        hashed_pw = make_password(data["password"])
        new_user = RegisteredUser.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"].strip().lower(),
            hashed_password=hashed_pw,
        )

        return {"message": f"User {new_user.username} successfully registered"}, 201

class Registered(User):
    def __init__(self, email_address, password):
        super().__init__(None, None)
        self.email_address = email_address.strip().lower()
        self.password = password

    def sign_in(self):
        user = RegisteredUser.objects.filter(email=self.email_address).first()
        if user and check_password(self.password, user.hashed_password):
            refresh = RefreshToken.for_user(user)
            return {
                "message": f"Welcome back, {user.first_name}!",
                "is_admin": user.is_admin,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, 200
        return {"error": "Invalid credentials"}, 401

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        data = json.loads(body_unicode)
        guest = Guest()
        response_data, status_code = guest.sign_up(data)
        return JsonResponse(response_data, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        body_unicode = request.body.decode("utf-8")
        data = json.loads(body_unicode)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"error": "Missing email or password"}, status=400)

        registered_user = Registered(email, password)
        response_data, status_code = registered_user.sign_in()

        if status_code == 200:
            user = RegisteredUser.objects.get(email=email)

            # Fetch dietary restrictions
            dietary_restrictions = list(user.dietary_restrictions.values_list("restriction", flat=True))

            # Store the token with time to expiry
            access_token = response_data["access"]
            expires_at = timezone.now() + timedelta(minutes=10)
            Token.objects.create(user=user, token=access_token, expires_at=expires_at)

            response_data.update({
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "skill_level": user.skill_level,
                "dietary_restrictions": dietary_restrictions,
            })
            return JsonResponse(response_data, status=status_code)

        return JsonResponse(response_data, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_user_data(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            
            #Token Checker
            db_token = Token.objects.filter(token=token).first()
            if not db_token or not db_token.is_valid():
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

            
            user = db_token.user
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            # User data
            dietary_restrictions = list(user.dietary_restrictions.values_list("restriction", flat=True))
            return JsonResponse({
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "skill_level": user.skill_level,
                "dietary_restrictions": dietary_restrictions,
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)

@csrf_exempt
@require_http_methods(["POST"])
def update_user_profile(request):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                user = RegisteredUser.objects.get(auth_token=token)
            except RegisteredUser.DoesNotExist:
                return JsonResponse({"error": "Invalid token"}, status=401)

            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)

            # Update skill level
            skill_level = data.get("skill_level")
            if skill_level and skill_level in [choice[0] for choice in SkillLevelChoices.choices]:
                user.skill_level = skill_level

            # Update dietary restrictions
            dietary_restrictions = data.get("dietary_restrictions", [])
            user.dietary_restrictions.all().delete()
            for restriction in dietary_restrictions:
                DietaryRestriction.objects.create(user=user, restriction=restriction)

            user.save()
            return JsonResponse({"success": "Profile updated successfully"}, status=200)
        else:
            return JsonResponse({"error": "Invalid token"}, status=401)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def logout_user(request):
    if request.method == "OPTIONS":
        response = HttpResponse(status=200)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Delete the token
            Token.objects.filter(token=token).delete()
            return JsonResponse({"message": "Logged out successfully"}, status=200)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)