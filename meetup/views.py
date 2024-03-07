from rest_framework.generics import ListAPIView
from .models import Interest
from .serializers import InterestSerializer

class InterestListView(ListAPIView):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
