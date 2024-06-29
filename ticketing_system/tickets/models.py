from django.db import models
from django.contrib.auth.models import User


class TicketType(models.Model):
    """defines my attributes of a ticket type"""

    name = models.CharField(max_length=100)
    max_users = models.PositiveIntegerField()

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

    def __str__(self):
        return f"{self.type.name} - {self.owner.username}"


class Invitation(models.Model):
    """defines the attributes of an invitation"""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
