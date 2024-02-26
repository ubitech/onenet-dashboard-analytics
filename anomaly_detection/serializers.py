from rest_framework import serializers
from anomaly_detection.models import Predictions

class PredictionsSerializer(serializers.ModelSerializer):
    timestamp_from = serializers.DateTimeField()
    timestamp_to = serializers.DateTimeField()
    ip = serializers.ListField(child=serializers.CharField())
    ip_status = serializers.ListField(child=serializers.FloatField())
    
    class Meta:
        model = Predictions
        fields = ('__all__')