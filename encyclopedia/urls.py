from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"), 
    path("<str:entry_title>", views.display_entry, name="entry_url"),
    path("search/", views.search_entry, name="search"),
    path("new/", views.new_page, name="new_page"),
    path("edit/<entry_title>", views.edit_content, name="edit"),
    path("random/", views.random_page, name="random"),
    path("random/<random_element>", views.random_entry, name="random_entry")
]
