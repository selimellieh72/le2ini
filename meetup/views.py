from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import MeetingRequest, TimeSlot, PlaceTimeRequest, Interest
from .serializers import MeetingRequestSerializer, PlaceTimeRequestSerializer,InterestSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

# helpers
def reset_acceptance(meeting_request, user_id):
    meeting_request.request_from_accepting = meeting_request.request_from.pk == user_id

    meeting_request.request_to_accepting = meeting_request.request_to.pk == user_id
    meeting_request.status = 'waiting'
    meeting_request.save()



class InterestListView(ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


class CreateMeetingRequestView(APIView):
    permission_classes = [IsAuthenticated]

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