from io import BytesIO
import qrcode
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from .models import GuestSection, Property, PropertyMembership
class GuestSectionInline(admin.StackedInline):
    model = GuestSection
    extra = 0
    fields = (
        "title",
        "slug",
        "icon",
        "content",
        "sort_order",
        "is_published",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    ordering = (
        "sort_order",
        "title",
    )
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "email",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "name",
        "slug",
        "email",
    )
    prepopulated_fields = {
        "slug": ("name",),
    }
    readonly_fields = (
        "created_at",
        "updated_at",
        "guest_portal_link",
        "qr_preview",
        "qr_download_link",
        "qr_card_link",
    )
    inlines = [
        GuestSectionInline,
    ]
    def guest_portal_link(self, obj):
        if not obj.pk:
            return "-"
        url = reverse(
            "properties:guest_portal",
            kwargs={"slug": obj.slug},
        )
        return format_html(
            '<a href="{}" target="_blank">Open guest portal</a>',
            url,
        )
    guest_portal_link.short_description = "Guest portal"
    def qr_preview(self, obj):
        if not obj.pk:
            return "-"
        url = reverse(
            "properties:property_qr",
            kwargs={"slug": obj.slug},
        )
        return format_html(
            '<img src="{}" width="160" height="160" alt="QR code">',
            url,
        )
    qr_preview.short_description = "QR code"
    def qr_download_link(self, obj):
            if not obj.pk:
                return "-"
            url = reverse(
                "properties:download_property_qr",
                kwargs={"slug": obj.slug},
            )
            return format_html(
                '<a href="{}">Download QR Code</a>',
                url,
            )
    qr_download_link.short_description = "Download QR"
    def qr_card_link(self, obj):
        if not obj.pk:
            return "-"
        url = reverse(
            "properties:qr_card",
            kwargs={"slug": obj.slug},
        )
        return format_html(
            '<a href="{}" target="_blank">Open printable QR card</a>',
            url,
        )
    qr_card_link.short_description = "QR card"
@admin.register(GuestSection)
class GuestSectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "property",
        "sort_order",
        "is_published",
        "updated_at",
    )
    list_filter = (
        "property",
        "is_published",
    )
    search_fields = (
        "title",
        "property__name",
        "content",
    )
    prepopulated_fields = {
        "slug": ("title",),
    }
    readonly_fields = (
        "created_at",
        "updated_at",
    )
@admin.register(PropertyMembership)
class PropertyMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "property",
        "role",
        "created_at",
    )
    list_filter = (
        "role",
        "property",
    )
    search_fields = (
        "user__username",
        "user__email",
        "property__name",
    )