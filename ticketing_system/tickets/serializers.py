from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, TicketType, Invitation


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "name", "max_users"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class TicketSerializer(serializers.ModelSerializer):
    type = TicketTypeSerializer()
    owner = UserSerializer()
    users = UserSerializer(many=True)

    class Meta:
        model = Ticket
        fields = ["id", "type", "owner", "users", "created_at"]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["type"]


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["id", "ticket", "email", "invited_by"]


class InvitationCreateSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=False
    )
