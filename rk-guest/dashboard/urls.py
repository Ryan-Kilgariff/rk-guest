from django.urls import path
from . import views
app_name = "dashboard"
urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "properties/<slug:slug>/",
        views.property_manage,
        name="property_manage",
    ),
    path(
        "properties/<slug:slug>/sections/add/",
        views.section_add,
        name="section_add",
    ),
    path(
        "properties/<slug:slug>/sections/<int:section_id>/edit/",
        views.section_edit,
        name="section_edit",
    ),
    path(
        "properties/<slug:slug>/sections/<int:section_id>/delete/",
        views.section_delete,
        name="section_delete",
    ),
    path(
        "properties/<slug:slug>/sections/<int:section_id>/move-up/",
        views.section_move_up,
        name="section_move_up",
    ),
    path(
        "properties/<slug:slug>/sections/<int:section_id>/move-down/",
        views.section_move_down,
        name="section_move_down",
    ),
    path(
        "properties/<slug:slug>/sections/reorder/",
        views.section_reorder,
        name="section_reorder",
    ),
]