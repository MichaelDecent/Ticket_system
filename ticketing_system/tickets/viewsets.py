import stripe
from ticketing_system import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .utils import send_inviatation_email
from .models import Ticket, TicketType, Invitation, Payment, Cart, CartItem
from django.contrib.auth.models import User
from .serializers import (
    TicketSerializer,
    TicketTypeSerializer,
    TicketCreateSerializer,
    UserSerializer,
    InvitationCreateSerializer,
    InvitationSerializer,
    PaymentSerializer,
    CartSerializer,
    CreateCartItemSerializer,
    PaymentCreateSerializer,
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
        ticket = serializer.save(owner=self.request.user, paid=False)
        ticket.users.add(self.request.user)
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["post"])
    def invite(self, request, pk=None):
        ticket = self.get_object()
        if not ticket.paid:
            return Response(
                {"status": "ticket not paid"}, status=status.HTTP_400_BAD_REQUEST
            )

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


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.request.user
        token = serializer.validated_data.get("stripe_token")
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                return Response(
                    {"status": "cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                )

            total_amount = sum(
                item.ticket.type.price * item.quantity for item in cart.items.all()
            )

            charge = stripe.Charge.create(
                amount=int(total_amount * 100),
                currency="usd",
                description=f"Ticket purchase for {user.username}",
                source=token,
                api_key=settings.STRIPE_SECRET_KEY,
            )

            payments = []
            for item in cart.items.all():
                payment = Payment.objects.create(
                    user=user,
                    ticket=item.ticket,
                    stripe_charge_id=charge["id"],
                    amount=item.ticket.type.price * item.quantity,
                )
                item.ticket.users.add(user)
                item.ticket.paid = True
                item.ticket.save()
                payments.append(payment)

            cart.items.all().delete()

            return Response(
                {
                    "status": "payment successful",
                    "payment": PaymentSerializer(payments, many=True).data,
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            return Response(
                {"status": "payment failed", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Cart.DoesNotExist:
            return Response(
                {"status": "cart not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateCartItemSerializer
        return CartSerializer

    def create(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        ticket_id = request.data.get("ticket_id")
        quantity = request.data.get("quantity")

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, ticket=ticket
            )
            if not created:
                cart_item.quantity += int(quantity)
                cart_item.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        except Ticket.DoesNotExist:
            return Response(
                {"status": "ticket not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk):
        cart_item = CartItem.objects.get(id=pk)
        self.perform_destroy(cart_item)
        return Response(status=status.HTTP_204_NO_CONTENT)
