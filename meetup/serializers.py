from .models import MeetingRequest, TimeSlot, PlaceRequest, Place, Interest
from authentication.models import User

from rest_framework import serializers


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


# Serializer for time slot requests
class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'meeting_request', 'slot', 'requested_by', 'requested_at']

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class PlaceRequestSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(write_only=True, required=False)
    place = PlaceSerializer(read_only=True)
    class Meta:
        model = PlaceRequest
        fields = ['id', 'meeting_request', 'place', 'requested_by', 'requested_at', 'place_name']
        extra_kwargs = {
                'place': {'read_only': True},
            
            }
    def create(self, validated_data):
        place_name = validated_data.pop('place_name', None)
        place, _ = Place.objects.get_or_create(name=place_name)
        validated_data['place'] = place
        return super().create(validated_data)

# Serializer for creating and updating meeting requests
class MeetingRequestSerializer(serializers.ModelSerializer):

    time_slots = serializers.SerializerMethodField()
    place_requests = serializers.SerializerMethodField()
    request_from = serializers.SerializerMethodField()
    request_to = serializers.SerializerMethodField()
    def get_request_from(self, obj):
        # Local import to avoid circular import
        from authentication.serializers import UserSerializer
        return UserSerializer(obj.request_from).data

    def get_request_to(self, obj):
        # Local import to avoid circular import
        from authentication.serializers import UserSerializer
        return UserSerializer(obj.request_to).data
    def get_time_slots(self, obj):
        queryset = obj.time_slots.all().order_by('-requested_at')
        return TimeSlotSerializer(queryset, many=True).data

    def get_place_requests(self, obj):
        # Assuming you have a PlaceRequestSerializer defined elsewhere
        queryset = obj.place_requests.all().order_by('-requested_at')
        return PlaceRequestSerializer(queryset, many=True).data

    class Meta:
        model = MeetingRequest
        fields = ['id', 'request_from', 'request_to', 'status', 'time_slots', 'place_requests'
                  ,'request_to_accepting', 'request_from_accepting']