from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from .models import RegisteredUser, Token

class Authenticator:
    def __init__(self, email_address=None, password=None):
        self.email_address = email_address.strip().lower() if email_address else None
        self.password = password

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

    def logout(self, token):
        Token.objects.filter(token=token).delete()  #Deletes token from database
        return {"message": "Logged out successfully"}, 200
