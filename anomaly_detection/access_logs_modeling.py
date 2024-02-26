import logging
import datetime
from django.apps import apps
from data_utilities.ml_procedures import IFClassification
from data_utilities.data_retrieval_procedure import historic_data_retrieval_and_preparation
from anomaly_detection.utils import convert_dict_for_serializer
from anomaly_detection.serializers import PredictionsSerializer
from anomaly_detection.ip_state_prediction import IpStatePrediction
from anomaly_detection.constants import number_of_days

logger = logging.getLogger(__name__)

def _fill_anomaly_detection_model_data(model, features):
    """
    Filling a dictionary structure with all the relevant to the anomaly detection model info 

    :param `str` model: The base64 binary form of the trained model decoded as ascii string
    :param `list` features: The features used for the model training

    :return `dict` anomaly_detection_model: The filled dictionary
    """

    logger.info('Starting the filling of the anomaly detection model info')

    try:
        trained_at = datetime.datetime.today().strftime('%Y.%m.%d')
        logger.debug(f'Model trained at: {trained_at}')
    except Exception as e:
        logger.error(f"Error generating trained_at timestamp: {str(e)}")
        return

    try:
        anomaly_detection_model = {
            "model": model,
            "trained_at": trained_at,
            "features_used": features
        }
        logger.debug(f'Anomaly detection model data: {anomaly_detection_model}')
    except Exception as e:
        logger.error(f"Error creating anomaly_detection_model dictionary: {str(e)}")
        return

    return anomaly_detection_model

def anomaly_detection_job():
    """
    This job will run once every number_of_days days to train an Isolation Forest Classifier to be used for predictions about normal/malicious IPs
    """
    
    logger.info('Starting the training of anomaly detection model')
    
    try:
        # get the elastic connector object
        elastic_search_config = apps.get_app_config('elastic')
    except Exception as e:
        logger.error(f"Error getting elastic search config: {str(e)}")
        return

    elastic_status = elastic_search_config.elastic_status
    if elastic_status == 'down':
        logger.error("ElasticSearch not available. Cronjob will not run.")
        return

    try:
        elastic_connector = elastic_search_config.elastic_connector
    except Exception as e:
        logger.error(f"Error establishing elastic connector: {str(e)}")
        return

    index = 'anomaly_detection_model'
    logger.debug(f"Index to be used: '{index}'")

    try:
        df_train, ips = historic_data_retrieval_and_preparation(number_of_days)
    except Exception as e:
        logger.error(f"Error retrieving and preparing historic data: {str(e)}")
        return
    
    if df_train.empty and not(ips):
        logger.warning(f"No new data available for training. The previous model will be used.")
        
    else:
        try:
            # classification training
            classification_job = IFClassification()
            classification_job.train_classifier(df_train)
        except Exception as e:
            logger.error(f"Error during classifier training: {str(e)}")
            return

        try:
            # fill doc with occupancy data
            train_data = _fill_anomaly_detection_model_data(classification_job.get_ifc_model_base64(), list(df_train.columns))
        except Exception as e:
            logger.error(f"Error filling anomaly detection model data: {str(e)}")
            return

        try:
            # store back the zone document
            elastic_connector.write_to_index(index, train_data)
        except Exception as e:
            logger.error(f"Error writing to index '{index}': {str(e)}")
            return

        logger.info(f'The model was saved successfully.')

def prediction_job():
    """
    This job will run once every batch_minutes minutes to predict if the IPs appear in these batch_minutes minutes are normal or malicious
    and save the results to postgres
    """

    logger.info('Starting the prediction of the latest access logs.')

    try: 
        ip_estimator = IpStatePrediction()
        predictions = ip_estimator.predict_ip_state()

        predictions_dict_final = convert_dict_for_serializer(predictions)
        serializer_result = PredictionsSerializer(data=predictions_dict_final)

        if serializer_result.is_valid():
            serializer_result.save()
            logger.info('Predictions saved successfully.')
        else:
            logger.debug("Error with data {}.".format(serializer_result.errors))
    except Exception as e:
        logger.exception(f"An error occurred during the prediction job: {str(e)}")