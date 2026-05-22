from rest_framework import serializers
from api.models import DataSource, RawData, Prediction, Alert

class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ["id", "name", "url", "is_active", "last_fetched", "created_at"]

class RawDataSerializer(serializers.ModelSerializer):
    # we include the source name as a string instead of just the id
    source_name = serializers.CharField(source="source.name", read_only=True)
    class Meta:
        model = RawData
        fields = ["id", "source_name", "timestamp", "value", "unit", "extra"]

class PredictionSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    class Meta:
        model = Prediction
        fields = ["id", "source_name", "predicted_at", "target_timestamp", "predicted_value", "confidence"]

class AlertSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    class Meta:
        model = Alert
        fields = ["id", "source_name", "timestamp", "message", "severity", "is_read"]