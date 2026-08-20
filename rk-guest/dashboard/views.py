from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.models import GuestSection, Property
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.text import slugify
import json
from django.http import JsonResponse
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
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
    portal_views = property_obj.portal_visits.filter(
        visited_at__gte=start_date,
    ).count()
    section_views = property_obj.section_views.filter(
        viewed_at__gte=start_date,
    )
    section_view_total = section_views.count()
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
            "analytics_period": analytics_period,
            "analytics_label": analytics_label,
            "portal_views": portal_views,
            "section_view_total": section_view_total,
            "section_stats": section_stats,
        },
    )
@login_required
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
        GuestSection.objects.create(
            property=property_obj,
            title=title,
            slug=section_slug,
            icon=request.POST.get("icon", "info"),
            content=content,
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
            "dashboard:property_manage",
            slug=property_obj.slug,
        )
    return render(
        request,
        "dashboard/section_form.html",
        {
            "property": property_obj,
            "section": None,
            "icon_choices": GuestSection.ICON_CHOICES,
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
        section.icon = request.POST.get(
            "icon",
            section.icon,
        )
        section.content = request.POST.get(
            "content",
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
            "dashboard:property_manage",
            slug=property_obj.slug,
        )
    return render(
        request,
        "dashboard/section_form.html",
        {
            "property": property_obj,
            "section": section,
            "icon_choices": GuestSection.ICON_CHOICES,
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