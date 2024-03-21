from django.urls import path
from .views import (
    InterestListView,
    CreateMeetingRequestView,
    RespondToMeetingRequestView,
   PlaceTimeRequestView,
    MeetingRequestsForUserView,
    MeetingRequestDetailView
)

urlpatterns = [
    # Interest List
    path('interests/', InterestListView.as_view(), name='interest-list'),
    
    # Create Meeting Request
    path('meeting-requests/create/<int:user_id>/', CreateMeetingRequestView.as_view(), name='create-meeting-request'),
    
    # Respond to Meeting Request (accept/reject)
    path('meeting-requests/respond/<int:meeting_request_id>/<str:action>/', RespondToMeetingRequestView.as_view(), name='respond-to-meeting-request'),
    
  
  
    # Check my meetings
    path('me/meeting-requests/', MeetingRequestsForUserView.as_view(), name='user-meeting-requests'),
    # Check meeting details
    path('meeting-requests/<int:meeting_request_id>/', MeetingRequestDetailView.as_view(), name='meeting-request-detail'),
      # Place Request
    path('meeting-requests/<int:meeting_request_id>/place-time-requests/', PlaceTimeRequestView.as_view(), name='time-place-request'),
]
    
