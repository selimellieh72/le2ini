from meetup.models import Interest, City
from meetup.serializers import InterestSerializer, CitySerializer
from .models import User, UserInfo, Avatar
from rest_framework import serializers
from rest_framework.fields import ListField

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_info = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = ( 'id', 'email', 'password', 'user_info', 'is_active')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    def get_user_info(self, obj):
        try:
            user_info = UserInfo.objects.get(user=obj)
            return UserInfoSerializer(user_info).data
        except UserInfo.DoesNotExist:
            return None



class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['id', 'image_url' ]

class UserInfoSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    interests_data = ListField(child=serializers.DictField(), write_only=True, required=False)
    city = CitySerializer()
    avatar = AvatarSerializer()
    # Use PrimaryKeyRelatedField for write operations
    avatar_id = serializers.PrimaryKeyRelatedField(queryset=Avatar.objects.all(), source='avatar', write_only=True, required=False)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source='city', write_only=True, required=False)
    
    # Use custom serializers for read operations
    avatar = AvatarSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    


    class Meta:
        model = UserInfo
        fields = ['full_name', 'date_of_birth', 'occupation', 'biography', 'interests', 'interests_data',
                'loc_lat', 'loc_lon', 'city', 'avatar', 'avatar_id', 'city_id']

    def create(self, validated_data):
        interests_data = validated_data.pop('interests_data', [])
        user_info = UserInfo.objects.create(**validated_data)
        for interest_data in interests_data:
            interest, _ = Interest.objects.get_or_create(**interest_data)
            user_info.interests.add(interest)
        return user_info

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests_data', None)
        instance = super().update(instance, validated_data)
        print(validated_data)

        if interests_data:
            instance.interests.clear()
            for interest_data in interests_data:
                interest, _ = Interest.objects.get_or_create(**interest_data)
                instance.interests.add(interest)
        
        return instance
