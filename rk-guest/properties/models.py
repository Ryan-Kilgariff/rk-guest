from django.db import models
from django.conf import settings
class Property(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to="property_logos/",
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    primary_colour = models.CharField(
        max_length=7,
        default="#000000",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    def get_guest_path(self):
        return f"/p/{self.slug}/"
class PropertyMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
    ]
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="property_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="manager",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("property", "user"),
                name="unique_property_user_membership",
            )
        ]
    def __str__(self):
        return (
            f"{self.user.username} — "
            f"{self.property.name} ({self.role})"
        )
class GuestSection(models.Model):
    ICON_CHOICES = [
    ("info", "Information"),
    ("wifi", "Wi-Fi"),
    ("breakfast", "Breakfast / Dining"),
    ("parking", "Parking"),
    ("checkout", "Check-in / Check-out"),
    ("facilities", "Facilities"),
    ("local", "Local Area"),
    ("faq", "FAQ"),
    ("contact", "Contact"),
    ]
    SECTION_TYPE_CHOICES = [
    ("generic", "General information"),
    ("wifi", "Wi-Fi"),
    ("stay_times", "Check-in / Check-out"),
    ("breakfast", "Breakfast / Dining"),
    ("parking", "Parking"),
    ("facilities", "Facilities"),
    ("local_area", "Local Area"),
    ("faq", "FAQ"),
    ]
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="guest_sections",
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    section_type = models.CharField(
        max_length=30,
        choices=SECTION_TYPE_CHOICES,
        default="generic",
    )
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default="info",
    )
    content = models.TextField(blank=True)
    wifi_network = models.CharField(
        max_length=150,
        blank=True,
    )
    wifi_password = models.CharField(
        max_length=150,
        blank=True,
    )
    check_in_time = models.CharField(
        max_length=50,
        blank=True,
    )
    check_out_time = models.CharField(
        max_length=50,
        blank=True,
    )
    check_times_note = models.CharField(
        max_length=255,
        blank=True,
    )
    breakfast_weekday_time = models.CharField(
        max_length=100,
        blank=True,
    )
    breakfast_weekend_time = models.CharField(
        max_length=100,
        blank=True,
    )
    breakfast_location = models.CharField(
        max_length=150,
        blank=True,
    )
    breakfast_note = models.CharField(
        max_length=255,
        blank=True,
    )
    parking_availability = models.CharField(
        max_length=150,
        blank=True,
    )
    parking_location = models.CharField(
        max_length=200,
        blank=True,
    )
    parking_registration = models.CharField(
        max_length=255,
        blank=True,
    )
    parking_note = models.CharField(
        max_length=255,
        blank=True,
    )
    copy_label = models.CharField(
        max_length=100,
        blank=True,
    )
    copy_value = models.CharField(
        max_length=255,
        blank=True,
    )
    action_label = models.CharField(
        max_length=100,
        blank=True,
    )
    action_url = models.URLField(
        blank=True,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = (
            "sort_order",
            "title",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("property", "slug"),
                name="unique_guest_section_slug_per_property",
            )
        ]
    def __str__(self):
        return f"{self.property.name} — {self.title}"
class GuestPortalVisit(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="portal_visits",
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
    )
    visited_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.property.name} — "
            f"{self.visited_at}"
        )
class GuestSectionView(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="section_views",
    )
    section = models.ForeignKey(
        GuestSection,
        on_delete=models.CASCADE,
        related_name="views",
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.property.name} — "
            f"{self.section.title}"
        )
class QRLocation(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="qr_locations",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = (
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=("property", "slug"),
                name="unique_qr_location_slug_per_property",
            )
        ]
    def __str__(self):
        return f"{self.property.name} — {self.name}"
class QRScan(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="qr_scans",
    )
    location = models.ForeignKey(
        QRLocation,
        on_delete=models.CASCADE,
        related_name="scans",
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        db_index=True,
    )
    scanned_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.property.name} — "
            f"{self.location.name}"
        )
class GuestSectionLink(models.Model):
    section = models.ForeignKey(
        GuestSection,
        on_delete=models.CASCADE,
        related_name="links",
    )
    label = models.CharField(
        max_length=100,
    )
    url = models.URLField()
    sort_order = models.PositiveIntegerField(
        default=0,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        ordering = (
            "sort_order",
            "id",
        )
    def __str__(self):
        return (
            f"{self.section.title} — "
            f"{self.label}"
        )
class GuestSectionItem(models.Model):
    section = models.ForeignKey(
        GuestSection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    title = models.CharField(
        max_length=150,
    )
    description = models.CharField(
        max_length=255,
        blank=True,
    )
    category = models.CharField(
        max_length=100,
        blank=True,
    )
    distance = models.CharField(
        max_length=100,
        blank=True,
    )
    url = models.URLField(
        blank=True,
    )
    link_label = models.CharField(
        max_length=100,
        blank=True,
    )
    sort_order = models.PositiveIntegerField(
        default=0,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        ordering = (
            "sort_order",
            "id",
        )
    def __str__(self):
        return (
            f"{self.section.title} — "
            f"{self.title}"
        )