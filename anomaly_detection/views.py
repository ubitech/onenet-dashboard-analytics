import logging
import datetime
from rest_framework.decorators import api_view
from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from django.utils import timezone
from anomaly_detection.serializers import PredictionsSerializer
from anomaly_detection.models import Predictions
from anomaly_detection.access_logs_modeling import anomaly_detection_job, prediction_job
from anomaly_detection.utils import predictions_to_frontend

logger = logging.getLogger(__name__)

@api_view(['POST'])
def trigger_training_cronjob(request):
    """
    Triggering manually the anomaly_detection_job
    """

    anomaly_detection_job()
    return Response(data="Cronjob finished. Check logs for more information. \n")

@api_view(['POST'])
def trigger_prediction_cronjob(request):
    """
    Triggering manually the prediction_job
    """

    prediction_job()
    return Response(data="Cronjob finished. Check logs for more information. \n")

@api_view(['GET'])
def get_predictions(request):
    """
    Retrieves the predictions from the database based on the 'minutes' argument from the request headers
    """
    
    # Extract the 'minutes' argument from the request headers
    minutes = request.headers.get('minutes')
    
    # Validate the 'minutes' argument
    if minutes not in ['20', '40', '60']:
        return HttpResponseBadRequest("Invalid 'minutes' value. It must be '20', '40', or '60'.")
    
    # Convert 'minutes' to integer
    minutes = int(minutes)
    
    # Calculate the datetime for the desired minutes in the past
    time_threshold = timezone.now() - timezone.timedelta(minutes=minutes)
    
    # Filter the Predictions objects based on the calculated time_threshold and now
    predictions_list = Predictions.objects.filter(timestamp_from__gte=time_threshold, timestamp_from__lte=timezone.now())
    
    # Serialize the queryset
    serializer = PredictionsSerializer(predictions_list, many=True)
    query = serializer.data
    
    # Convert the serialized data to the desired format for the frontend
    data_to_frontend = predictions_to_frontend(query)
   
    # Return the data to the frontend
    return Response(data_to_frontend)