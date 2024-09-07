from django.db import models
from authentication.models import User

# Create your models here.
class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)


    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class MeetingRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('waiting', 'Waiting'),
        ('declined', 'Declined'),
        ('accepted', 'Accepted'),
    ]
    request_from = models.ForeignKey(User, related_name='meeting_requests_sent', on_delete=models.CASCADE)
    request_to = models.ForeignKey(User, related_name='meeting_requests_received', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('request_from', 'request_to')

    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending')
    request_from_accepting = models.BooleanField(default=False)
    request_to_accepting = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    
class TimeSlot(models.Model):
    TIME_SLOTS = [
    ('08:00', '08:00 - 08:30'),
    ('08:30', '08:30 - 09:00'),
    ('09:00', '09:00 - 09:30'),
    ('09:30', '09:30 - 10:00'),
    ('10:00', '10:00 - 10:30'),
    ('10:30', '10:30 - 11:00'),
    ('11:00', '11:00 - 11:30'),
    ('11:30', '11:30 - 12:00'),
    ('12:00', '12:00 - 12:30'),
    ('12:30', '12:30 - 13:00'),
    ('13:00', '13:00 - 13:30'),
    ('13:30', '13:30 - 14:00'),
    ('14:00', '14:00 - 14:30'),
    ('14:30', '14:30 - 15:00'),
    ('15:00', '15:00 - 15:30'),
    ('15:30', '15:30 - 16:00'),
    ('16:00', '16:00 - 16:30'),
    ('16:30', '16:30 - 17:00'),
    ('17:00', '17:00 - 17:30'),
    ('17:30', '17:30 - 18:00'),
    ('18:00', '18:00 - 18:30'),
    ]
    # meeting_request = models.ForeignKey(MeetingRequest, related_name='time_slots', on_delete=models.CASCADE)
    slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    # requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # requested_at = models.DateTimeField(auto_now_add=True)

class Place(models.Model):
    name = models.CharField(max_length=255)

class PlaceTimeRequest(models.Model):
    meeting_request = models.ForeignKey(MeetingRequest, related_name='place_time_requests', on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    time = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    
