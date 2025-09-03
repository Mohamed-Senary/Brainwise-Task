from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data.get("username", ""),
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user

#Adding the role of each user in the response with the token
#reduces queries on db to get role of user
#will ease permissions later
class CustomTokenObtainPairSerializer (TokenObtainPairSerializer):
    @classmethod
    def get_token (cls, user):
        token = super().get_token(user)

        token['role'] = user.role
        token['username'] = user.username

        return token