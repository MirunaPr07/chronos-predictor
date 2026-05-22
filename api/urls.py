from django.urls import path
from api import views

urlpatterns = [
    path("sources/", views.DataSourceListView.as_view(), name="sources"),
    path("data/", views.RawDataListView.as_view(), name="raw-data"),
    path("predictions/", views.PredictionListView.as_view(), name="predictions"),
    path("alerts/", views.AlertListView.as_view(), name="alerts"),
    path("threads/status/", views.ThreadStatusView.as_view(), name="thread-status"),
    path("threads/start/", views.StartCollectorsView.as_view(), name="start-collectors"),
    path("threads/stop/", views.StopCollectorsView.as_view(), name="stop-collectors"),
]