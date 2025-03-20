from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RegisteredUser, DietaryRestriction, Token
from .models import SkillLevelChoices

class profileManager:
    def __init__(self, user=None):
        self.user = user
    
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
 