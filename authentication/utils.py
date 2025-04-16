import random
import os
import string
from django.core.mail import send_mail
from django.utils import timezone

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def generate_verification_code(size=4):
    return ''.join(random.choices(string.digits, k=size))


def send_verification_email(user):
    return_value = False

    if user.verification_code:
        return_value = True

    user.verification_code = generate_verification_code()
    user.code_sent_at = timezone.now()
    user.save()

    # Setup Brevo API config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare template-based email
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{
            "email": user.email,
 
        }],
        template_id=int(os.getenv("BREVO_TEMPLATE_ID")),
        params={
      
            "code": user.verification_code,
        },
        sender={
            "name": os.getenv("DEFAULT_FROM_USER"),
            "email": os.getenv("DEFAULT_FROM_EMAIL"),
        }
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent via Brevo template:", response)
    except ApiException as e:
        print("Brevo API Exception:", e)

    return return_value