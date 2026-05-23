from django.urls import path
from dashboard import views

urlpatterns = [
    path("", views.index, name="dashboard-index"),
    path("predictions/", views.predictions_view, name="dashboard-predictions"),
]