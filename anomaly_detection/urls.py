from django.urls import path
import anomaly_detection.views as views

urlpatterns = [
    path('trigger_training_cronjob/', views.trigger_training_cronjob, name = 'trigger_training_cronjob'),
    path('trigger_prediction_cronjob/', views.trigger_prediction_cronjob, name = 'trigger_prediction_cronjob'),
    path('get_predictions/', views.get_predictions, name = 'get_predictions'),
]