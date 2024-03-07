from django.urls import path
from .views import InterestListView 

urlpatterns = [
    path('interests/', InterestListView.as_view(), name='interest-list'),  # Use the correct view class name
]