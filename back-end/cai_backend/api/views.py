"""
    Overall refactoring notes:
    Adjust each class based on its notes
    Test debug at every step along the way
    Refactor the classes to live OUTSIDE this file

    Go over functionality, make sure everything is present
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services.authenticator import Authenticator
from .services.profile_manager import ProfileManager
from .services.ai_engine import AIEngine
from .services.recipe_parser import RecipeParser
from .services.save_manager import SaveManager

import json


@csrf_exempt
@require_http_methods(["GET","POST"])
def generate_recipe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            if not all(key in data for key in ["ingredients", "skill_level", "time"]):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            # Run the engine with prompt
            ai_engine = AIEngine()
            recipe_json = ai_engine.generate_recipe_json(
                skill_level=data["skill_level"],
                available_time=data["time"],
                dietary_restrictions=data["dietary_restrictions"],
                ingredients=data["ingredients"]
            )

            # Could also index inside the parser object
            parser = RecipeParser(recipe_json)
            parser.to_file("saved_recipe.json")
            parser.update_data(recipe_json["recipe"])

        except (json.JSONDecodeError, TypeError) as je:
            return JsonResponse({"error": f"failed to load JSON {je}"}, status=400)
        
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
        
        # Save the recipe to user history IF LOGGED IN
        # Doesn't work
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            print(token)
            if token:
                save_manager = SaveManager.from_token(token)
                recipe = parser.to_model()
                save_manager.add_to_history(recipe)  
        
        return JsonResponse(recipe_json)
        

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
        auth = Authenticator()
        response_data, status_code = auth.sign_up(data)
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

        authenticate_user = Authenticator(email, password)
        response_data, status_code = authenticate_user.sign_in()
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
        prof_man = ProfileManager()
        response_data, status_code = prof_man.get_user_data(token)
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
            prof_man = ProfileManager()
            response_data, status_code = prof_man.update_profile(token, data)
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
            authenticate_user = Authenticator()
            response_data, status_code = authenticate_user.logout(token)
            return JsonResponse(response_data, status=status_code)
        else:
            return JsonResponse({"error": "Authorization header missing or invalid"}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def save_button(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]

            # Once you check if history is saving, instead of parsing from file
            # Pull latest recipe from user history
            parser = RecipeParser.from_file("saved_recipe.json")
            recipe = parser.to_model() # type: ignore
            save_manager = SaveManager.from_token(token)
            recipe = save_manager.save_recipe(recipe)

            return JsonResponse({"message": "Recipe saved successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def view_recipes(request):
     if request.method == "GET":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            save_manager = SaveManager.from_token(token)
            json_recipes = save_manager.view_saved_recipes()
            

            return JsonResponse({"saved_recipes": json_recipes}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)