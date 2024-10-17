# utils.py
import random
import os
import string
from django.core.mail import send_mail
from django.utils import timezone
from mailersend import emails



def generate_verification_code(size=4):
    return ''.join(random.choices(string.digits, k=size))

def send_verification_email(user):
    return_value = False
    if user.verification_code:
        return_value = True
    user.verification_code = generate_verification_code()
    user.code_sent_at = timezone.now()
    user.save()
    mailer = emails.NewEmail(os.getenv("MAILERSEND_API_KEY"))

    
    mail_body = {}

    mail_from = {
        "name": os.getenv("DEFAULT_FROM_USER"),
        "email": os.getenv("DEFAULT_FROM_EMAIL"),
    }

    recipients = [
        {
          
            "email": user.email,
        }
    ]

    variables = [
        {
            "email": user.email,
            "data": {
          
                "code": user.verification_code,
            },
            "substitutions": {
                "code": user.verification_code,
            
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Verification Code From Le2ini", mail_body)
    mailer.set_template("0r83ql3kpex4zw1j", mail_body)
    mailer.set_personalization(variables, mail_body)

    print(mailer.send(mail_body))


    return return_value
