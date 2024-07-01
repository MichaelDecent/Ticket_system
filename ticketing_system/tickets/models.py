from django.db import models
from django.contrib.auth.models import User


class TicketType(models.Model):
    """defines my attributes of a ticket type"""

    name = models.CharField(max_length=100)
    max_users = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    "defienes the attribute of a particular ticket"
    type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User, related_name="owned_tickets", on_delete=models.CASCADE
    )
    users = models.ManyToManyField(User, related_name="tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.type.name} - {self.owner.username}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.ticket.type.name} in {self.cart.user.username}'s cart"


class Invitation(models.Model):
    """defines the attributes of an invitation"""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation for {self.email} to {self.ticket.type.name}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    stripe_charge_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticket.type.name} - {self.amount}"
