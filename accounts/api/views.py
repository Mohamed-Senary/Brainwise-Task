from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.api.serializers import UserAccountSerializer

User = get_user_model()

@api_view(['POST'])
def register_user (request):
    serializer = UserAccountSerializer (data=request.data)
    serializer.is_valid(raise_exception = True)
    user = serializer.save()
    return Response(serializer.data , status = status.HTTP_201_CREATED)
    