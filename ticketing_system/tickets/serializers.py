from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, TicketType, Invitation, Payment, Cart, CartItem


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ["id", "name", "max_users", "price"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]


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
    emails = serializers.ListField(child=serializers.EmailField(), allow_empty=False)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "ticket", "stripe_charge_id", "amount", "created_at"]


class PaymentCreateSerializer(serializers.Serializer):
    stripe_token = serializers.CharField()


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "ticket", "quantity"]


class CreateCartItemSerializer(serializers.Serializer):
    ticket_id = serializers.IntegerField()
    quantity = serializers. IntegerField()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "created_at", "updated_at"]
