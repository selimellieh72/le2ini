from meetup.serializers import InterestSerializer
from .models import User, UserInfo
from meetup.models import Interest
from rest_framework import serializers
from rest_framework.fields import ListField

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_info = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = ( 'id', 'email', 'password', 'user_info')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    def get_user_info(self, obj):
        try:
            user_info = UserInfo.objects.get(user=obj)
            return UserInfoSerializer(user_info).data
        except UserInfo.DoesNotExist:
            return None



class UserInfoSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    interests_data = ListField(child=serializers.DictField(), write_only=True, required=False)
    


    class Meta:
        model = UserInfo
        fields = ['full_name', 'date_of_birth', 'occupation', 'biography', 'interests', 'interests_data']

    def create(self, validated_data):
        interests_data = validated_data.pop('interests_data', [])
        user_info = UserInfo.objects.create(**validated_data)
        for interest_data in interests_data:
            interest, _ = Interest.objects.get_or_create(**interest_data)
            user_info.interests.add(interest)
        return user_info

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests_data', [])
        instance = super().update(instance, validated_data)
        print(validated_data)

        # Clear existing interests and add the new ones
        instance.interests.clear()
        for interest_data in interests_data:
            interest, _ = Interest.objects.get_or_create(**interest_data)
            instance.interests.add(interest)
        return instance

