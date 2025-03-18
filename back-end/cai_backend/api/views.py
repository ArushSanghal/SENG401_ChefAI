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

        hashed_pw = make_password(data["password"])  #Creates a hashed password
        new_user = RegisteredUser.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"].strip().lower(),
            hashed_password=hashed_pw,
        )

        return {"message": f"User {new_user.username} successfully registered"}, 201

class Registered(User):
    def __init__(self, email_address=None, password=None, user=None):
        super().__init__(None, None)
        self.email_address = email_address.strip().lower() if email_address else None
        self.password = password
        self.user = user

    def sign_in(self):
        user = RegisteredUser.objects.filter(email=self.email_address).first()
        if user and check_password(self.password, user.hashed_password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            expires_at = timezone.now() + timedelta(minutes=10)

            #Token In Database
            Token.objects.create(user=user, token=access_token, expires_at=expires_at)

            return {
                "message": f"Welcome back, {user.first_name}!",
                "is_admin": user.is_admin,
                "refresh": str(refresh),
                "access": access_token,
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "skill_level": user.skill_level,
                "dietary_restrictions": list(user.dietary_restrictions.values_list("restriction", flat=True)),
            }, 200
        return {"error": "Invalid credentials"}, 401

    def get_user_data(self, token):
        db_token = Token.objects.filter(token=token).first()   #Checks token
        if not db_token or not db_token.is_valid():
            return {"error": "Invalid or expired token"}, 401

        user = db_token.user
        if not user:
            return {"error": "User not found"}, 404

        return {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "skill_level": user.skill_level,
            "dietary_restrictions": list(user.dietary_restrictions.values_list("restriction", flat=True)),
        }, 200

    def update_profile(self, token, data):
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user_id = validated_token["user_id"]

            user = RegisteredUser.objects.filter(id=user_id).first()
            if not user:
                return {"error": "User not found"}, 404

            #Skill level
            skill_level = data.get("skill_level")
            if skill_level and skill_level in [choice[0] for choice in SkillLevelChoices.choices]:
                user.skill_level = skill_level

            #Dietary restrictions
            dietary_restrictions = data.get("dietary_restrictions", [])
            user.dietary_restrictions.all().delete()
            for restriction in dietary_restrictions:
                DietaryRestriction.objects.create(user=user, restriction=restriction)

            user.save()
            return {"success": "Profile updated successfully"}, 200
        except (InvalidToken, TokenError) as e:
            print(f"Token error: {e}")
            return {"error": "Invalid token"}, 401

    def logout(self, token):
        Token.objects.filter(token=token).delete()  #Deletes token from database
        return {"message": "Logged out successfully"}, 200





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
        registered_user = Registered()
        response_data, status_code = registered_user.get_user_data(token)
        return JsonResponse(response_data, status=status_code)
    else:
        return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def update_user_profile(request):
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)
            registered_user = Registered()
            response_data, status_code = registered_user.update_profile(token, data)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
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
            registered_user = Registered()
            response_data, status_code = registered_user.logout(token)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)