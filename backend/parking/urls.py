from django.urls import path

from . import views


urlpatterns = [
    path("entry/", views.entry),
    path("exit/", views.exit_parking),
    path("dashboard/", views.dashboard),
]