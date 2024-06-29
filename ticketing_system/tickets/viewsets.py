from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .utils import send_inviatation_email
from .models import Ticket, TicketType, Invitation
from django.contrib.auth.models import User
from .serializers import (
    TicketSerializer,
    TicketTypeSerializer,
    TicketCreateSerializer,
    UserSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
)


class TicketTypeViewSet(viewsets.ModelViewSet):
    queryset = TicketType.objects.all()
    serializer_class = TicketTypeSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return TicketCreateSerializer
        elif self.action == "invite":
            return InvitationCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save(owner=self.request.user)
        ticket.users.add(self.request.user)

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        ticket = self.get_object()
        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails = serializer.validated_data.get("emails")

        invited_count = ticket.users.count()
        max_users = ticket.type.max_users
        invitations = []

        for email in emails:
            if invited_count < max_users:
                invitation = Invitation.objects.create(
                    ticket=ticket, email=email, invited_by=request.user
                )
                send_inviatation_email(invitation, request)
                invitations.append(invitation)
                invited_count += 1
            else:
                return Response(
                    {"status": "ticket full"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {
                "status": "invitations sent",
                "invitations": InvitationSerializer(invitations, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
