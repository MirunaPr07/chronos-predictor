from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import DataSource, RawData, Prediction, Alert

from api.serializers import (
    DataSourceSerializer,
    RawDataSerializer,
    PredictionSerializer,
    AlertSerializer,
)

# returns all data sources we have in the db:
class DataSourceListView(APIView):
    def get(self, request):
        sources = DataSource.objects.all()
        serializer = DataSourceSerializer(sources, many=True)
        return Response(serializer.data)

# returns the latest 100 raw data points, optionally filtered by source
class RawDataListView(APIView):
    def get(self, request):
        source_name = request.query_params.get("source", None)
        data = RawData.objects.all()[:100]
        if source_name:
            data = RawData.objects.filter(
                source__name=source_name
            )[:100]
        serializer = RawDataSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        # we allow external sources to push data directly to the API
        serializer = RawDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# returns the latest predictions from the LSTM model
class PredictionListView(APIView):
    def get(self, request):
        source_name = request.query_params.get("source", None)
        predictions = Prediction.objects.all()[:50]
        if source_name:
            predictions = Prediction.objects.filter(
                source__name=source_name
            )[:50]
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

class AlertListView(APIView):
    # returns all alerts, filtered by severity
    def get(self, request):
        severity = request.query_params.get("severity", None)
        alerts = Alert.objects.all()[:50]
        if severity:
            alerts = Alert.objects.filter(severity=severity)[:50]
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

class ThreadStatusView(APIView):
    # we expose the thread manager status, so the dashboard can display it
    def get(self, request):
        from collectors.thread_manager import ThreadManager
        manager = ThreadManager()
        return Response(manager.status())


class StartCollectorsView(APIView):
    # we start all collector threads via the API
    def post(self, request):
        from collectors.thread_manager import ThreadManager
        manager = ThreadManager()
        manager.start_all()
        return Response({"message": "all collectors started"})

class StopCollectorsView(APIView):
    # we stop all collector threads via the API
    def post(self, request):
        from collectors.thread_manager import ThreadManager
        manager = ThreadManager()
        manager.stop_all()
        return Response({"message": "all collectors stopped"})