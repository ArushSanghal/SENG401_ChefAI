from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.authtoken.models import Token
from .models import RegisteredUser, DietaryRestriction, SkillLevelChoices

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
            return {"error": "Password must be at least 8 characters long."}, 400  # ✅ Password validation

        if RegisteredUser.objects.filter(username=data["username"]).exists():
            return {"error": "Username already exists. Please choose another one."}, 400  # ✅ Username validation

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
            return {"message": f"Welcome back, {user.first_name}!", "is_admin": user.is_admin}, 200
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
            user.generate_token()  # Generate a token manually

            # Fetch dietary restrictions
            dietary_restrictions = list(user.dietary_restrictions.values_list("restriction", flat=True))

            response_data.update({
                "token": user.auth_token,
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
    users = RegisteredUser.objects.all().values("first_name", "last_name", "email", "username")
    return JsonResponse(list(users), safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def update_user_profile(request):
    try:
        auth_token = request.headers.get("Authorization").split(" ")[1]
        user = RegisteredUser.objects.filter(auth_token=auth_token).first()

        if not user:
            return JsonResponse({"error": "Invalid token"}, status=401)

        body_unicode = request.body.decode("utf-8")
        data = json.loads(body_unicode)

        # Update skill level
        skill_level = data.get("skill_level")
        if skill_level and skill_level in [choice[0] for choice in SkillLevelChoices.choices]:
            user.skill_level = skill_level

        # Update dietary restrictions
        dietary_restrictions = data.get("dietary_restrictions", [])
        user.dietary_restrictions.all().delete()  # Remove existing restrictions
        for restriction in dietary_restrictions:
            DietaryRestriction.objects.create(user=user, restriction=restriction)

        user.save()
        return JsonResponse({"success": "Profile updated successfully"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
