import qrcode
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Property
def guest_portal(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
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