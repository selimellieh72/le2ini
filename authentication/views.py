from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, UserInfo
from .serializers import UserSerializer, UserInfoSerializer
from .models import UserInfo

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id=None):
        # If no user_id is provided, default to the current user's UserInfo
        if user_id is None:
            userinfo = get_object_or_404(UserInfo, user=request.user)
        else:
            # Fetch the UserInfo for the given user_id
            userinfo = get_object_or_404(UserInfo, user__id=user_id)
        serializer = UserInfoSerializer(userinfo)
        return Response(serializer.data)
    def post(self, request):
        # Check if UserInfo already exists for the user
        if UserInfo.objects.filter(user=request.user).exists():
            # If it exists, instruct to use PATCH for updates
            return Response({"detail": "UserInfo already exists. Use PATCH request to update."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Explicitly assign the user here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        userinfo = get_object_or_404(UserInfo, user=request.user)  # Ensure it's the user's own UserInfo
        serializer = UserInfoSerializer(userinfo, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
