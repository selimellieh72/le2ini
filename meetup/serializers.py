from .models import MeetingRequest, TimeSlot, Place, Interest, PlaceTimeRequest
from authentication.models import User

from rest_framework import serializers
from django.shortcuts import get_object_or_404

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']


# Serializer for time slot requests
class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class PlaceTimeRequestSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(write_only=True, required=False)
    place = PlaceSerializer(read_only=True)
    time_slot = serializers.CharField(write_only=True, required=False)
    time = TimeSlotSerializer(read_only=True)
    class Meta:
        model = PlaceTimeRequest
        fields = ['id', 'meeting_request', 'place', 'requested_by', 'requested_at', 'place_name', 'time_slot', 'time']
        extra_kwargs = {
                'place': {'read_only': True},
            
            }
    def create(self, validated_data):
        place_name = validated_data.pop('place_name', None)
        # Assuming Place.objects.get_or_create() is satisfactory for your use case
        place, _ = Place.objects.get_or_create(name=place_name)

        time_name = validated_data.pop('time_slot', None)
        # Use filter().first() to avoid raising an exception if no match is found
        time, _ = TimeSlot.objects.get_or_create(slot=time_name)
        
        if time is None:
            # If no TimeSlot is found, raise a validation error
            raise serializers.ValidationError({'message': 'Time slot does not exist.'})
        
    

        validated_data['place'] = place
        validated_data['time'] = time

        return super().create(validated_data)

# Serializer for creating and updating meeting requests
class MeetingRequestSerializer(serializers.ModelSerializer):
    request_from = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    request_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


    place_time_requests = PlaceTimeRequestSerializer(many=True, read_only=True)
 
    class Meta:
        model = MeetingRequest
        fields = ['id', 'request_from', 'request_to', 'status', 'place_time_requests', 'request_from_accepting', 'request_to_accepting']
