from .models import User, UserInfo
from meetup.models import Interest
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_info = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = ( 'email', 'password', 'user_info')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    def get_user_info(self, obj):
        try:
            user_info = UserInfo.objects.get(user=obj)
            return UserInfoSerializer(user_info).data
        except UserInfo.DoesNotExist:
            return None



class UserInfoSerializer(serializers.ModelSerializer):
    interests = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Interest.objects.all(), required=False
    )

    class Meta:
        model = UserInfo
        fields = ['full_name', 'date_of_birth', 'occupation', 'biography', 'interests']

    def create(self, validated_data):
        interests_data = validated_data.pop('interests', [])
        user_info = UserInfo.objects.create(**validated_data)
        user_info.interests.set(interests_data)
        return user_info

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests', [])
        instance = super().update(instance, validated_data)
        instance.interests.set(interests_data)
        return instance