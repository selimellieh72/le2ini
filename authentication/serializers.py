from .models import User, UserInfo
from meetup.models import Interest
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ( 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)



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