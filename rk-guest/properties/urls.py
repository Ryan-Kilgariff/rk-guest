from django.urls import path
from . import views
app_name = "properties"
urlpatterns = [
    path(
        "p/<slug:slug>/",
        views.guest_portal,
        name="guest_portal",
    ),
    path(
        "p/<slug:slug>/qr/",
        views.property_qr,
        name="property_qr",
    ),
    path(
        "p/<slug:slug>/qr/download/",
        views.download_property_qr,
        name="download_property_qr",
    ),
    path(
        "p/<slug:slug>/qr/card/",
        views.qr_card,
        name="qr_card",
    ),
]