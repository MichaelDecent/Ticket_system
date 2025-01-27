from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Invitation


class AcceptInvitationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, invitation_id):
        try:
            invitation = Invitation.objects.get(id=invitation_id)
            if not invitation.accepted:
                try:
                    user = User.objects.get(email=invitation.email)
                except User.DoesNotExist:
                    user = User.objects.create_user(
                        username=invitation.email.split("@")[0],
                        email=invitation.email,
                        password=User.objects.make_random_password(),
                    )
                invitation.ticket.users.add(user)
                invitation.accepted = True
                invitation.save()
                return Response(
                    {"status": "invitation accepted"}, status=status.HTTP_200_OK
                )
            return Response(
                {"status": "invitation already accepted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Invitation.DoesNotExist:
            return Response(
                {"status": "invalid invitation"}, status=status.HTTP_400_BAD_REQUEST
            )
