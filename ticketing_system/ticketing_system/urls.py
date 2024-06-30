from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from tickets.views import AcceptInvitationView
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from tickets.viewsets import (
    TicketTypeViewSet,
    TicketViewSet,
    UserViewSet,
    PaymentViewSet,
    CartItemViewSet,
    CartViewSet,
)


schema_view = get_schema_view(
    openapi.Info(
        title="Ticket System API",
        default_version="v1",
        description="A RESTful API that manages a Ticketing sysytem",
    ),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
)

router = DefaultRouter()
router.register(r"ticket-types", TicketTypeViewSet)
router.register(r"tickets", TicketViewSet)
router.register(r"users", UserViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"carts", CartViewSet, basename="cart")
router.register(r"cart-items", CartItemViewSet, basename="cartitem")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/v1/invitations/accept/<int:invitation_id>/",
        AcceptInvitationView.as_view(),
        name="accept_invitation",
    ),
]
