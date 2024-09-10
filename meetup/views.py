from authentication.models import UserInfo
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import MeetingRequest, TimeSlot, PlaceTimeRequest, Interest
from .serializers import  MeetingRequestSerializer, PlaceTimeRequestSerializer,InterestSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from authentication.serializers import UserSerializer
from django.db.models import Count
from django.db.models import Prefetch, Q
from geopy.distance import distance as geopy_distance
from django.db.models import F
from django.db.models.expressions import RawSQL
# helpers
def reset_acceptance(meeting_request, user_id):
    meeting_request.request_from_accepting = meeting_request.request_from.pk == user_id

    meeting_request.request_to_accepting = meeting_request.request_to.pk == user_id
    meeting_request.status = 'waiting'
    meeting_request.save()



class InterestListView(ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
   
# lookup users, paginated by 10, with "for you" interests
# which means, ordered by, most common interests with the authenticated user

class ForYouLookupUsersView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        User = get_user_model()
        current_user = self.request.user
        current_user_info = current_user.info
        current_user_interests = current_user_info.interests.all().values_list('id', flat=True)

        # Prefetch interests directly on the User model
        users = User.objects.exclude(id=current_user.id,
                                
        ).prefetch_related(
          'info'
        )

        # Annotate users with the number of common interests
        users_with_similarity = users.annotate(
            similarity_score=Count(
                'info__interests',
                filter=Q(info__interests__in=current_user_interests)
            )
        ).order_by('-similarity_score')

        return users_with_similarity
    
class NearbyLookupUsersView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        User = get_user_model()
        current_user = self.request.user
        current_user_info = current_user.info

        if current_user_info.loc_lat is None or current_user_info.loc_lon is None:
            return User.objects.none()

        delta = float(self.request.query_params.get('delta', 10))  # distance in kilometers
        current_lat = current_user_info.loc_lat
        current_lon = current_user_info.loc_lon

        # Haversine formula to calculate distance
        haversine = """
        6371 * acos(
            cos(radians(%s)) * cos(radians(loc_lat)) * 
            cos(radians(loc_lon) - radians(%s)) + 
            sin(radians(%s)) * sin(radians(loc_lat))
        )
        """

        distance_raw_sql = RawSQL(haversine, (current_lat, current_lon, current_lat))

        # Filter users within the delta distance and exclude the current user
        nearby_users = User.objects.exclude(id=current_user.id).filter(
            info__isnull=False,
            info__loc_lat__isnull=False,
            info__loc_lon__isnull=False,
        ).annotate(distance=distance_raw_sql).filter(distance__lte=delta).order_by('distance')

        return nearby_users
class CreateMeetingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    # get meeting by id
    def get(self, request, meeting_id):
        meeting = get_object_or_404(MeetingRequest, pk=meeting_id)
        serializer = MeetingRequestSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        print({"request_from": request.user.pk, "request_to":user_id })
        serializer = MeetingRequestSerializer(data={"request_from": request.user.pk, "request_to":user_id })
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Successfully sent request', 'meeting_request': serializer.data}, status=status.HTTP_201_CREATED)
        # Return error message if the serializer is not valid
        return Response({'message': "Cannot send request at this time"}, status=status.HTTP_400_BAD_REQUEST)
class RespondToMeetingRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_request_id, action):
        meeting_request = get_object_or_404(MeetingRequest, pk=meeting_request_id)

        # Default response message
        response_message = "No action taken."

        if action == 'accept':
            if meeting_request.status == 'pending' and request.user == meeting_request.request_to:
                # Move from pending to waiting when request_to accepts.
                meeting_request.status = 'waiting'
                response_message = "Meeting request accepted. Awaiting further actions."
            elif meeting_request.status == 'waiting':
                # First make sure we have TimePlaceRequests associated with the meeting request.
                if meeting_request.place_time_requests.count() == 0:
                    return Response({'message': 'Cannot accept without a time and place proposal.'}, status=status.HTTP_400_BAD_REQUEST)
                # Check which user is accepting and mark their acceptance.
                if request.user == meeting_request.request_from:
                    meeting_request.request_from_accepting = True
                    response_message = "Time/Place accepted by the requester. Awaiting acceptance from the other user."
                elif request.user == meeting_request.request_to:
                    meeting_request.request_to_accepting = True
                    response_message = "Time/Place accepted by the invitee. Awaiting acceptance from the other user."

                # If both have accepted the proposed time and place, move to accepted.
                if meeting_request.request_from_accepting and meeting_request.request_to_accepting:
                    meeting_request.status = 'accepted'
                    response_message = "Meeting successfully scheduled."
        elif action == 'reject':
            meeting_request.status = 'declined'
            response_message = "Meeting request declined."
            # Optionally, handle deletion or further state changes here.
        
        meeting_request.save()
        return Response({'status': meeting_request.status, 'message': response_message}, status=status.HTTP_200_OK)


class MeetingRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, meeting_request_id):
        meeting_request = get_object_or_404(MeetingRequest, pk=meeting_request_id)
        
        # Check if the current user is part of the meeting request
        if request.user not in [meeting_request.request_from, meeting_request.request_to]:
            return Response({'message': 'You do not have permission to view this meeting request.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Serialize the meeting request, including time slots and place requests
        serializer = MeetingRequestSerializer(meeting_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PlaceTimeRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_request_id):
        
        meeting_request = MeetingRequest.objects.filter(pk=meeting_request_id).first()

        if meeting_request is None:
            return Response({'message': 'Meeting request not found.'}, status=status.HTTP_404_NOT_FOUND)
   
        # Check if the user is part of the meeting and if the status is 'waiting'
        if request.user not in [meeting_request.request_from, meeting_request.request_to] or meeting_request.status != 'waiting':
            return Response({'message': 'You cannot make this request at this time.'}, status=status.HTTP_403_FORBIDDEN)
   
        serializer = PlaceTimeRequestSerializer(data={'requested_by': request.user.pk, 'meeting_request': meeting_request_id, 'place_name': request.data['place_name'], 'time_slot': request.data['time_slot'] })
        if serializer.is_valid():
            
            reset_acceptance(meeting_request, request.user.pk)
            
            serializer.save()
           
            return Response(serializer.data, status=status.HTTP_201_CREATED)
      
        return Response({'message': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)
       
class MeetingRequestsForUserView(ListAPIView):
    serializer_class = MeetingRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return meeting requests where the authenticated user is the target
        return MeetingRequest.objects.filter(Q(request_to=self.request.user) | Q(request_from=self.request.user)).prefetch_related('place_time_requests')
    
