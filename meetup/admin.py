from django.contrib import admin
from .models import Interest, City, MeetingRequest, TimeSlot
# Register your models here.
admin.site.register(Interest)
admin.site.register(City)
admin.site.register(MeetingRequest)
admin.site.register(TimeSlot)