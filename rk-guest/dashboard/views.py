from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.models import (
    GuestSectionLink,
    GuestSectionItem,
    GuestSection,
    Property,
    QRLocation,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.text import slugify
import json
from django.http import JsonResponse
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
@login_required
def home(request):
    properties = Property.objects.filter(
        memberships__user=request.user,
        is_active=True,
    ).distinct().order_by("name")
    context = {
        "properties": properties,
    }
    return render(
        request,
        "dashboard/home.html",
        context,
    )
@login_required
def property_manage(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    if request.method == "POST":
        property_obj.name = request.POST.get(
            "name",
            property_obj.name,
        ).strip()
        property_obj.description = request.POST.get(
            "description",
            "",
        ).strip()
        property_obj.phone = request.POST.get(
            "phone",
            "",
        ).strip()
        property_obj.email = request.POST.get(
            "email",
            "",
        ).strip()
        property_obj.website = request.POST.get(
            "website",
            "",
        ).strip()
        property_obj.address = request.POST.get(
            "address",
            "",
        ).strip()
        property_obj.primary_colour = request.POST.get(
            "primary_colour",
            property_obj.primary_colour,
        ).strip()
        if request.FILES.get("logo"):
            property_obj.logo = request.FILES["logo"]
        property_obj.save()
        return redirect(
            "dashboard:property_manage",
            slug=property_obj.slug,
        )
    analytics_period = request.GET.get(
        "period",
        "30",
    )
    now = timezone.now()
    if analytics_period == "today":
        local_now = timezone.localtime(now)
        start_date = local_now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        analytics_label = "Today"
    elif analytics_period == "7":
        start_date = now - timedelta(days=7)
        analytics_label = "Last 7 days"
    else:
        analytics_period = "30"
        start_date = now - timedelta(days=30)
        analytics_label = "Last 30 days"
    # -----------------------------------------
    # Guest portal analytics
    # -----------------------------------------
    portal_visit_queryset = (
        property_obj.portal_visits
        .filter(
            visited_at__gte=start_date,
        )
    )
    portal_views = portal_visit_queryset.count()
    unique_guest_sessions = (
        portal_visit_queryset
        .exclude(session_key="")
        .values("session_key")
        .distinct()
        .count()
    )
    # -----------------------------------------
    # Guest section analytics
    # -----------------------------------------
    section_views = (
        property_obj.section_views
        .filter(
            viewed_at__gte=start_date,
        )
    )
    section_view_total = section_views.count()
    engaged_sessions = (
        section_views
        .exclude(session_key="")
        .values("session_key")
        .distinct()
        .count()
    )
    if unique_guest_sessions:
        engagement_rate = round(
            (
                engaged_sessions
                / unique_guest_sessions
            )
            * 100
        )
    else:
        engagement_rate = 0
    qr_scan_queryset = (
        property_obj.qr_scans
        .filter(
            scanned_at__gte=start_date,
        )
    )
    qr_scan_total = qr_scan_queryset.count()
    qr_location_stats = (
        qr_scan_queryset
        .values(
            "location__id",
            "location__name",
            "location__is_active",
        )
        .annotate(
            scan_count=Count("id"),
        )
        .order_by("-scan_count")
    )
    section_stats = (
        section_views
        .values(
            "section__id",
            "section__title",
        )
        .annotate(
            view_count=Count("id"),
        )
        .order_by("-view_count")
    )
    return render(
        request,
        "dashboard/property_manage.html",
        {
            "property": property_obj,
            "sections": property_obj.guest_sections.all(),
            "qr_locations": property_obj.qr_locations.all(),
            "analytics_period": analytics_period,
            "analytics_label": analytics_label,
            "portal_views": portal_views,
            "unique_guest_sessions": unique_guest_sessions,
            "section_view_total": section_view_total,
            "engaged_sessions": engaged_sessions,
            "engagement_rate": engagement_rate,
            "section_stats": section_stats,
            "qr_scan_total": qr_scan_total,
            "qr_location_stats": qr_location_stats,
        },
    )
@login_required
def section_add(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        if not title:
            messages.error(
                request,
                "Section title is required.",
            )
            return redirect(
                "dashboard:section_add",
                slug=property_obj.slug,
            )
        duplicate = GuestSection.objects.filter(
            property=property_obj,
            title__iexact=title,
        ).exists()
        if duplicate:
            messages.error(
                request,
                "A section with this title already exists.",
            )
            return redirect(
                "dashboard:section_add",
                slug=property_obj.slug,
            )
        section_slug = slugify(title)
        section = GuestSection.objects.create(
            property=property_obj,
            title=title,
            slug=section_slug,
            section_type=request.POST.get(
                "section_type",
                "generic",
            ),
            icon=request.POST.get("icon", "info"),
            content=content,
            wifi_network=request.POST.get(
                "wifi_network",
                "",
            ).strip(),
            wifi_password=request.POST.get(
                "wifi_password",
                "",
            ).strip(),
            check_in_time=request.POST.get(
                "check_in_time",
                "",
            ).strip(),
            check_out_time=request.POST.get(
                "check_out_time",
                "",
            ).strip(),
            check_times_note=request.POST.get(
                "check_times_note",
                "",
            ).strip(),
            breakfast_weekday_time=request.POST.get(
                "breakfast_weekday_time",
                "",
            ).strip(),
            breakfast_weekend_time=request.POST.get(
                "breakfast_weekend_time",
                "",
            ).strip(),
            breakfast_location=request.POST.get(
                "breakfast_location",
                "",
            ).strip(),
            breakfast_note=request.POST.get(
                "breakfast_note",
                "",
            ).strip(),
            parking_availability=request.POST.get(
                "parking_availability",
                "",
            ).strip(),
            parking_location=request.POST.get(
                "parking_location",
                "",
            ).strip(),
            parking_registration=request.POST.get(
                "parking_registration",
                "",
            ).strip(),
            parking_note=request.POST.get(
                "parking_note",
                "",
            ).strip(),
            copy_label=request.POST.get(
                "copy_label",
                "",
            ).strip(),
            copy_value=request.POST.get(
                "copy_value",
                "",
            ).strip(),
            sort_order=request.POST.get(
                "sort_order",
                0,
            ),
            is_published=(
                request.POST.get("is_published") == "on"
            ),
        )
        messages.success(
            request,
            f"{title} was added successfully.",
        )
        return redirect(
            reverse(
                "dashboard:section_edit",
                kwargs={
                    "slug": property_obj.slug,
                    "section_id": section.id,
                },
            )
            + "#section-manager"
        )
    return render(
        request,
        "dashboard/section_form.html",
        {
            "property": property_obj,
            "section": None,
            "icon_choices": GuestSection.ICON_CHOICES,
            "section_type_choices": GuestSection.SECTION_TYPE_CHOICES,
        },
    )
@login_required
def section_edit(request, slug, section_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        title = request.POST.get(
            "title",
            "",
        ).strip()
        if not title:
            messages.error(
                request,
                "Section title is required.",
            )
            return redirect(
                "dashboard:section_edit",
                slug=property_obj.slug,
                section_id=section.id,
            )
        duplicate = GuestSection.objects.filter(
            property=property_obj,
            title__iexact=title,
        ).exclude(
            id=section.id,
        ).exists()
        if duplicate:
            messages.error(
                request,
                "A section with this title already exists.",
            )
            return redirect(
                "dashboard:section_edit",
                slug=property_obj.slug,
                section_id=section.id,
            )
        section.title = title
        section.slug = slugify(title)
        section.section_type = request.POST.get(
            "section_type",
            section.section_type,
        )
        section.icon = request.POST.get(
            "icon",
            section.icon,
        )
        section.content = request.POST.get(
            "content",
            "",
        ).strip()
        section.wifi_network = request.POST.get(
            "wifi_network",
            "",
        ).strip()
        section.wifi_password = request.POST.get(
            "wifi_password",
            "",
        ).strip()
        section.check_in_time = request.POST.get(
            "check_in_time",
            "",
        ).strip()
        section.check_out_time = request.POST.get(
            "check_out_time",
            "",
        ).strip()
        section.check_times_note = request.POST.get(
            "check_times_note",
            "",
        ).strip()
        section.breakfast_weekday_time = request.POST.get(
            "breakfast_weekday_time",
            "",
        ).strip()
        section.breakfast_weekend_time = request.POST.get(
            "breakfast_weekend_time",
            "",
        ).strip()
        section.breakfast_location = request.POST.get(
            "breakfast_location",
            "",
        ).strip()
        section.breakfast_note = request.POST.get(
            "breakfast_note",
            "",
        ).strip()
        section.parking_availability = request.POST.get(
            "parking_availability",
            "",
        ).strip()
        section.parking_location = request.POST.get(
            "parking_location",
            "",
        ).strip()
        section.parking_registration = request.POST.get(
            "parking_registration",
            "",
        ).strip()
        section.parking_note = request.POST.get(
            "parking_note",
            "",
        ).strip()
        section.copy_label = request.POST.get(
            "copy_label",
            "",
        ).strip()
        section.copy_value = request.POST.get(
            "copy_value",
            "",
        ).strip()
        section.sort_order = request.POST.get(
            "sort_order",
            section.sort_order,
        )
        section.is_published = (
            request.POST.get("is_published") == "on"
        )
        section.save()
        messages.success(
            request,
            f"{section.title} was updated successfully.",
        )
        return redirect(
            reverse(
                "dashboard:section_edit",
                kwargs={
                    "slug": property_obj.slug,
                    "section_id": section.id,
                },
            )
            + "#section-manager"
        )
    return render(
        request,
        "dashboard/section_form.html",
        {
            "property": property_obj,
            "section": section,
            "icon_choices": GuestSection.ICON_CHOICES,
            "section_type_choices": GuestSection.SECTION_TYPE_CHOICES,
        },
    )
@login_required
def section_delete(request, slug, section_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        section_title = section.title
        section.delete()
        messages.success(
            request,
            f"{section_title} was deleted.",
        )
    return redirect(
        "dashboard:property_manage",
        slug=property_obj.slug,
    )
@login_required
def section_move_up(request, slug, section_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        previous_section = (
            property_obj.guest_sections
            .filter(sort_order__lt=section.sort_order)
            .order_by("-sort_order")
            .first()
        )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    return redirect(
        "dashboard:property_manage",
        slug=property_obj.slug,
    )
@login_required
def section_move_down(request, slug, section_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        next_section = (
            property_obj.guest_sections
            .filter(sort_order__gt=section.sort_order)
            .order_by("sort_order")
            .first()
        )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    return redirect(
        "dashboard:property_manage",
        slug=property_obj.slug,
    )
@login_required
def section_reorder(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=405,
        )
    try:
        data = json.loads(request.body)
        section_ids = data.get("section_ids", [])
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {"error": "Invalid request data."},
            status=400,
        )
    valid_sections = {
        section.id: section
        for section in property_obj.guest_sections.filter(
            id__in=section_ids,
        )
    }
    if len(valid_sections) != len(section_ids):
        return JsonResponse(
            {"error": "Invalid guest section."},
            status=400,
        )
    for index, section_id in enumerate(section_ids, start=1):
        section = valid_sections.get(section_id)
        if section:
            section.sort_order = index * 10
            section.save(
                update_fields=["sort_order"],
            )
    return JsonResponse(
        {
            "success": True,
        }
    )
@login_required
def qr_location_add(request, slug):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()
        if not name:
            messages.error(
                request,
                "QR location name is required.",
            )
            return redirect(
                "dashboard:qr_location_add",
                slug=property_obj.slug,
            )
        location_slug = slugify(name)
        duplicate = QRLocation.objects.filter(
            property=property_obj,
            slug=location_slug,
        ).exists()
        if duplicate:
            messages.error(
                request,
                "A QR location with this name already exists.",
            )
            return redirect(
                "dashboard:qr_location_add",
                slug=property_obj.slug,
            )
        QRLocation.objects.create(
            property=property_obj,
            name=name,
            slug=location_slug,
            is_active=True,
        )
        messages.success(
            request,
            f"{name} QR location was created.",
        )
        return redirect(
            "dashboard:property_manage",
            slug=property_obj.slug,
        )
    return render(
        request,
        "dashboard/qr_location_form.html",
        {
            "property": property_obj,
            "location": None,
        },
    )
@login_required
def qr_location_edit(request, slug, location_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    location = get_object_or_404(
        QRLocation,
        id=location_id,
        property=property_obj,
    )
    if request.method == "POST":
        name = request.POST.get(
            "name",
            "",
        ).strip()
        if not name:
            messages.error(
                request,
                "QR location name is required.",
            )
            return redirect(
                "dashboard:qr_location_edit",
                slug=property_obj.slug,
                location_id=location.id,
            )
        location_slug = slugify(name)
        duplicate = (
            QRLocation.objects
            .filter(
                property=property_obj,
                slug=location_slug,
            )
            .exclude(
                id=location.id,
            )
            .exists()
        )
        if duplicate:
            messages.error(
                request,
                "A QR location with this name already exists.",
            )
            return redirect(
                "dashboard:qr_location_edit",
                slug=property_obj.slug,
                location_id=location.id,
            )
        location.name = name
        location.slug = location_slug
        location.is_active = (
            request.POST.get("is_active") == "on"
        )
        location.save()
        messages.success(
            request,
            f"{location.name} was updated successfully.",
        )
        return redirect(
            "dashboard:property_manage",
            slug=property_obj.slug,
        )
    return render(
        request,
        "dashboard/qr_location_form.html",
        {
            "property": property_obj,
            "location": location,
        },
    )
@login_required
def qr_location_detail(request, slug, location_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    location = get_object_or_404(
        QRLocation,
        id=location_id,
        property=property_obj,
    )
    return render(
        request,
        "dashboard/qr_location_detail.html",
        {
            "property": property_obj,
            "location": location,
        },
    )
@login_required
def qr_location_delete(request, slug, location_id):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    location = get_object_or_404(
        QRLocation,
        id=location_id,
        property=property_obj,
    )
    if request.method == "POST":
        location_name = location.name
        location.delete()
        messages.success(
            request,
            f"{location_name} QR location was deleted.",
        )
    return redirect(
        "dashboard:property_manage",
        slug=property_obj.slug,
    )
@login_required
def section_link_add(
    request,
    slug,
    section_id,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        label = request.POST.get(
            "link_label",
            "",
        ).strip()
        url = request.POST.get(
            "link_url",
            "",
        ).strip()
        if not label or not url:
            messages.error(
                request,
                "Both the link label and URL are required.",
            )
            return redirect(
                "dashboard:section_edit",
                slug=property_obj.slug,
                section_id=section.id,
            )
        last_link = (
            section.links
            .order_by("-sort_order")
            .first()
        )
        next_order = (
            last_link.sort_order + 10
            if last_link
            else 10
        )
        GuestSectionLink.objects.create(
            section=section,
            label=label,
            url=url,
            sort_order=next_order,
            is_active=True,
        )
        messages.success(
            request,
            f"{label} was added.",
        )
    return redirect(
        reverse(
            "dashboard:section_edit",
            kwargs={
                "slug": property_obj.slug,
                "section_id": section.id,
            },
        )
        + "#section-links"
    )
@login_required
def section_link_delete(
    request,
    slug,
    section_id,
    link_id,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    link = get_object_or_404(
        GuestSectionLink,
        id=link_id,
        section=section,
    )
    if request.method == "POST":
        label = link.label
        link.delete()
        messages.success(
            request,
            f"{label} was removed.",
        )
    return redirect(
        reverse(
            "dashboard:section_edit",
            kwargs={
                "slug": property_obj.slug,
                "section_id": section.id,
            },
        )
        + "#section-links"
    )
@login_required
def section_item_add(
    request,
    slug,
    section_id,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    if request.method == "POST":
        title = request.POST.get(
            "item_title",
            "",
        ).strip()
        description = request.POST.get(
            "item_description",
            "",
        ).strip()
        category = request.POST.get(
            "item_category",
            "",
        ).strip()
        distance = request.POST.get(
            "item_distance",
            "",
        ).strip()
        url = request.POST.get(
            "item_url",
            "",
        ).strip()
        link_label = request.POST.get(
            "item_link_label",
            "",
        ).strip()
        if not title:
            messages.error(
                request,
                "Facility name is required.",
            )
            return redirect(
                reverse(
                    "dashboard:section_edit",
                    kwargs={
                        "slug": property_obj.slug,
                        "section_id": section.id,
                    },
                )
                + "#section-items"
            )
        last_item = (
            section.items
            .order_by("-sort_order")
            .first()
        )
        next_order = (
            last_item.sort_order + 10
            if last_item
            else 10
        )
        GuestSectionItem.objects.create(
            section=section,
            title=title,
            description=description,
            category=category,
            distance=distance,
            url=url,
            link_label=link_label,
            sort_order=next_order,
            is_active=True,
        )
        messages.success(
            request,
            f"{title} was added.",
        )
    return redirect(
        reverse(
            "dashboard:section_edit",
            kwargs={
                "slug": property_obj.slug,
                "section_id": section.id,
            },
        )
        + "#section-items"
    )
@login_required
def section_item_edit(
    request,
    slug,
    section_id,
    item_id,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    item = get_object_or_404(
        GuestSectionItem,
        id=item_id,
        section=section,
    )
    if request.method == "POST":
        title = request.POST.get(
            "item_title",
            "",
        ).strip()
        description = request.POST.get(
            "item_description",
            "",
        ).strip()
        category = request.POST.get(
            "item_category",
            "",
        ).strip()
        distance = request.POST.get(
            "item_distance",
            "",
        ).strip()
        url = request.POST.get(
            "item_url",
            "",
        ).strip()
        link_label = request.POST.get(
            "item_link_label",
            "",
        ).strip()
        is_active = (
            request.POST.get("is_active") == "on"
        )
        if not title:
            messages.error(
                request,
                "Facility name is required.",
            )
            return redirect(
                reverse(
                    "dashboard:section_item_edit",
                    kwargs={
                        "slug": property_obj.slug,
                        "section_id": section.id,
                        "item_id": item.id,
                    },
                )
            )
        item.title = title
        item.description = description
        item.is_active = is_active
        item.category = category
        item.distance = distance
        item.url = url
        item.link_label = link_label
        item.save()
        messages.success(
            request,
            f"{item.title} was updated.",
        )
        return redirect(
            reverse(
                "dashboard:section_edit",
                kwargs={
                    "slug": property_obj.slug,
                    "section_id": section.id,
                },
            )
            + "#section-items"
        )
    return render(
        request,
        "dashboard/section_item_form.html",
        {
            "property": property_obj,
            "section": section,
            "item": item,
        },
    )
@login_required
def section_item_delete(
    request,
    slug,
    section_id,
    item_id,
):
    property_obj = get_object_or_404(
        Property,
        slug=slug,
        is_active=True,
        memberships__user=request.user,
    )
    section = get_object_or_404(
        GuestSection,
        id=section_id,
        property=property_obj,
    )
    item = get_object_or_404(
        GuestSectionItem,
        id=item_id,
        section=section,
    )
    if request.method == "POST":
        title = item.title
        item.delete()
        messages.success(
            request,
            f"{title} was removed.",
        )
    return redirect(
        reverse(
            "dashboard:section_edit",
            kwargs={
                "slug": property_obj.slug,
                "section_id": section.id,
            },
        )
        + "#section-items"
    )