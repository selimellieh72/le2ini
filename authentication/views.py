from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Avatar, User, UserInfo
from .serializers import AvatarSerializer, UserSerializer, UserInfoSerializer
from django.utils import timezone
from django.contrib.auth import authenticate
from .utils import send_verification_email
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q





class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email(user)
            return Response({"user": serializer.data,  "message": "Check your email for the verification code."}, status=status.HTTP_201_CREATED)
        
        
        # Check if the email is already taken
        if 'email' in serializer.errors:
            return Response({"message": "Email already taken."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Email or password incorrect. Try again later."}, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        # Check if the password is correct
        if user.check_password(password):
            if not user.is_active:
                if not send_verification_email(user):
                    return Response({"message": "Check your email for the verification code."})
                else:
                    return Response({"message": "Sent another verification code email."})
            else:
                return Response({"message": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
class LoginUserView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                token_serializer = self.get_serializer(data={'email': email, 'password': password})
                if token_serializer.is_valid():
                    return Response({
                        'access': token_serializer.validated_data.get('access'),
                        'refresh': token_serializer.validated_data.get('refresh')
                    })
            else:
                return Response({"message": "User is not verified."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class UserInfoView(APIView):
   
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            return  [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get(self, request, user_id=None):
      
        # If no user_id is provided, default to the current user's UserInfo
        if user_id is None:
            print(request.user.id)
            userinfo = get_object_or_404(UserInfo, user=request.user)
        else:
            # Fetch the UserInfo for the given user_id
            userinfo = get_object_or_404(UserInfo, user__id=user_id)
        serializer = UserInfoSerializer(userinfo)
        return Response({**serializer.data, 'id': userinfo.user.id, 'email': userinfo.user.email})
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the password is correct
        if user.check_password(password):
            # Proceed if the user is not active (assuming they are unverified)
        
            if UserInfo.objects.filter(user=user).exists():
                return Response({"message": "UserInfo already exists. Please verify your email to update your info."}, status=status.HTTP_400_BAD_REQUEST)

            # Exclude email and password from the serializer data
            mutable_data = request.data.copy()
            mutable_data.pop('email', None)
            mutable_data.pop('password', None)

            serializer = UserInfoSerializer(data=mutable_data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({**serializer.data, "email": email, "password": password , 'id': user.id}, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        
    def patch(self, request):
        userinfo =  get_object_or_404(UserInfo, user=request.user)  # Ensure it's the user's own UserInfo
        serializer = UserInfoSerializer(userinfo, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email, verification_code=code)
        except User.DoesNotExist:
            return Response({"message": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() - user.code_sent_at <= timezone.timedelta(minutes=30):  # 30 minutes validity
            user.is_active = True
            user.verification_code = None
            user.save()
         


            token_serializer = TokenObtainPairSerializer(data={'email': email, 'password': password
                                                               })

            if token_serializer.is_valid():
                return Response({
                    'access': token_serializer.validated_data.get('access'),
                    'refresh': token_serializer.validated_data.get('refresh'),
                    'message': "Email verified successfully."
                })
            return Response({"ok": "ok"})
        else:
            return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)

class LookupUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):

     

        # add to exclude yourself too!
        # exclude also those with no info
        last_50_users =  User.objects.exclude(Q(meeting_requests_sent__request_to=request.user) | Q(meeting_requests_received__request_from=request.user) | Q(id=request.user.id) | Q(info__isnull=True)).order_by('-last_login')[:50]
        serializer = UserSerializer(last_50_users, many=True)
        return Response(serializer.data)
    

class ResetPasswordView(APIView):
    def patch(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not request.user.check_password(current_password):
            return Response({"message": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Password updated successfully."})
    
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response({"message": "User is not verified."}, status=status.HTTP_400_BAD_REQUEST)
        if not send_verification_email(user):
            return Response({"message": "Check your email for the verification code."})
        else:
            return Response({"message": "Sent another verification code email."})
        
    def patch(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            user = User.objects.get(email=email, verification_code=code)
        except User.DoesNotExist:
            return Response({"message": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"message": "User is not verified."}, status=status.HTTP_400_BAD_REQUEST)
        if timezone.now() - user.code_sent_at <= timezone.timedelta(minutes=30):  # 30 minutes validity
            user.verification_code = None
            password = request.data.get('password')
            user.set_password(password)
            user.save()
            return Response({"message": "Verification code is correct. Updated password successfully."})
        else:
            return Response({"message": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
        
class CheckOtpValidityView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            user = User.objects.get(email=email, verification_code=code)
        except User.DoesNotExist:
            return Response({"message": "Invalid email or verification code."}, status=status.HTTP_400_BAD_REQUEST)
        if timezone.now() - user.code_sent_at <= timezone.timedelta(minutes=30):  # 30 minutes validity
            return Response({"message": "Verification code is correct."})
        else:
            return Response({"message": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
        
class AvatarListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer