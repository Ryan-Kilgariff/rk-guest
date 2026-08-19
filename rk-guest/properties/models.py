from django.db import models
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
class GuestSection(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="guest_sections",
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField()
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
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default="info",
    )
    content = models.TextField(blank=True)
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