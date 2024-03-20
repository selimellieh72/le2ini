from .models import MeetingRequest, TimeSlot, PlaceRequest, Place, Interest
from django.contrib.auth.models import User
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

class PlaceRequestSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(write_only=True, required=False)

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
    time_slots = TimeSlotSerializer(many=True, read_only=True, required=False)
    place_requests = PlaceRequestSerializer(many=True, read_only=True, required=False)


    class Meta:
        model = MeetingRequest
        fields = ['id', 'request_from', 'request_to', 'status', 'time_slots', 'place_requests'
                  ,'request_to_accepting', 'request_from_accepting']