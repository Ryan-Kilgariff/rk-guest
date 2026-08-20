import qrcode
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import (
    GuestPortalVisit,
    GuestSection,
    GuestSectionView,
    Property,
    QRLocation,
    QRScan,
)
def get_guest_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key
def guest_portal(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    session_key = get_guest_session_key(request)
    GuestPortalVisit.objects.create(
        property=property_obj,
        session_key=session_key,
    )
    sections = property_obj.guest_sections.filter(
        is_published=True,
    )
    context = {
        "property": property_obj,
        "sections": sections,
    }
    return render(
        request,
        "properties/guest_portal.html",
        context,
    )
def property_qr(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    guest_url = request.build_absolute_uri(
        property_obj.get_guest_path()
    )
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(guest_url)
    qr.make(fit=True)
    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    response = HttpResponse(content_type="image/png")
    image.save(
        response,
        format="PNG",
    )
    return response
def download_property_qr(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    guest_url = request.build_absolute_uri(
        property_obj.get_guest_path()
    )
    qr = qrcode.QRCode(
        version=1,
        box_size=12,
        border=4,
    )
    qr.add_data(guest_url)
    qr.make(fit=True)
    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    response = HttpResponse(
        content_type="image/png"
    )
    filename = f"{property_obj.slug}-rk-guest-qr.png"
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    image.save(
        response,
        format="PNG",
    )
    return response
def qr_card(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    return render(
        request,
        "properties/qr_card.html",
        {
            "property": property_obj,
        },
    )
def track_section_view(request, slug, section_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405,
        )
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
        is_published=True,
    )
    session_key = get_guest_session_key(request)
    GuestSectionView.objects.create(
        property=property_obj,
        section=section,
        session_key=session_key,
    )
    return JsonResponse(
        {"success": True}
    )
def qr_location_redirect(request, slug, location_slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    location = get_object_or_404(
        QRLocation,
        property=property_obj,
        slug=location_slug,
        is_active=True,
    )
    session_key = get_guest_session_key(request)
    QRScan.objects.create(
        property=property_obj,
        location=location,
        session_key=session_key,
    )
    guest_url = reverse(
        "properties:guest_portal",
        kwargs={
            "slug": property_obj.slug,
        },
    )
    return redirect(guest_url)
def qr_location_image(request, slug, location_slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    location = get_object_or_404(
        QRLocation,
        property=property_obj,
        slug=location_slug,
        is_active=True,
    )
    location_path = reverse(
        "properties:qr_location_redirect",
        kwargs={
            "slug": property_obj.slug,
            "location_slug": location.slug,
        },
    )
    qr_url = request.build_absolute_uri(
        location_path
    )
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    response = HttpResponse(
        content_type="image/png"
    )
    image.save(
        response,
        format="PNG",
    )
    return response
def download_qr_location_image(
    request,
    slug,
    location_slug,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    location = get_object_or_404(
        QRLocation,
        property=property_obj,
        slug=location_slug,
        is_active=True,
    )
    location_path = reverse(
        "properties:qr_location_redirect",
        kwargs={
            "slug": property_obj.slug,
            "location_slug": location.slug,
        },
    )
    qr_url = request.build_absolute_uri(
        location_path
    )
    qr = qrcode.QRCode(
        version=1,
        box_size=12,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )
    response = HttpResponse(
        content_type="image/png"
    )
    filename = (
        f"{property_obj.slug}-"
        f"{location.slug}-rk-guest-qr.png"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )
    image.save(
        response,
        format="PNG",
    )
    return response
def qr_location_card(
    request,
    slug,
    location_slug,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
    )
    location = get_object_or_404(
        QRLocation,
        property=property_obj,
        slug=location_slug,
        is_active=True,
    )
    return render(
        request,
        "properties/qr_location_card.html",
        {
            "property": property_obj,
            "location": location,
        },
    )