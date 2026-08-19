from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from properties.models import Property
@login_required
def home(request):
    properties = Property.objects.filter(
        is_active=True,
    ).order_by("name")
    context = {
        "properties": properties,
    }
    return render(
        request,
        "dashboard/home.html",
        context,
    )