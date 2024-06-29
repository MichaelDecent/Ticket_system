from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string


def send_inviatation_email(invitation, request):
    subject = "You have been invited to a ticket"
    html_content = render_to_string(
        "invitation_email.html",
        {
            "inviter": invitation.invited_by.username,
            "ticket_type": invitation.ticket.type.name,
            "accept_url": request.build_absolute_uri(reverse(
                "accept_invitation", args=[invitation.id])
            ),
        },
    )
    msg = EmailMultiAlternatives(
        subject, html_content, settings.EMAIL_HOST_USER, [invitation.email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
