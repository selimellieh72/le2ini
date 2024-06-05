# utils.py
import random
import string
from django.core.mail import send_mail
from django.utils import timezone

def generate_verification_code(size=4):
    return ''.join(random.choices( string.digits, k=size))

def send_verification_email(user):
    return_value = False
    if user.verification_code:
        return_value = True
    user.verification_code = generate_verification_code()
    user.code_sent_at = timezone.now()
    user.save()
    subject = 'Your Verification Code'
    message = f'Your verification code is: {user.verification_code}'
    send_mail(subject, message, 'from@yourdomain.com', [user.email])
    return return_value
