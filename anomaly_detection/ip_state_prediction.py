import logging
import pandas as pd
from django.apps import apps
import datetime
from data_utilities.ml_procedures import IFClassification
from data_utilities.data_retrieval_procedure import historic_data_retrieval_and_preparation_prediction
from elastic.utils import get_anomaly_detection_model
from anomaly_detection.constants import batch_minutes


logger = logging.getLogger(__name__)

class IpStatePrediction():
    """
    IpStatePrediciton is responsible for predicting if an IP is malicious or normal
    """

    def __init__(self):
        self.classifier = IFClassification()
        self.elastic_search_config = apps.get_app_config('elastic')

    def load_stored_model(self):
        """
        Load a trained model from elastic and decode it in order to be used for prediction

        :return `list` features_used: The features used by the classifier to train the model       
        """

        logger.info("Loading the stored model.")

        try:
            anomaly_model_data = get_anomaly_detection_model()

            if len(anomaly_model_data) == 0:
                logger.error("There is no previous data in index.")
                return 

            anomaly_model = anomaly_model_data["model"]
            features_used = anomaly_model_data["features_used"]

            self.classifier.get_ifc_model_from_base64(anomaly_model)
            logger.info("Stored model loaded successfully.")

            return features_used
        
        except Exception as e:
            logger.exception(f"Error loading stored model: {str(e)}")
            return 

    def predict_ip_state(self):
        """
        Predict the state of an ip using a stored model

        :return `list` ip_predict_list: The dictionary containing the results of the prediction, which has the form [timestamps_list, current_ips_list, predicted_ip_state_list], 
                                        where {ip_state: -1 (for malicious) or 1 (for normal)}
        """

        logger.info("Predicting IP state.")

        try:
            features_used = self.load_stored_model()

            start = datetime.datetime.now()
            end = start + datetime.timedelta(minutes=batch_minutes)

            if len(features_used) == 0:
                logger.debug(f"The index of the anomaly detection model wasn't found.")
                ip_predict_list = [start, end, [], []]

                return ip_predict_list

            current_data_df, current_ips = historic_data_retrieval_and_preparation_prediction(batch_minutes)

            if current_data_df.empty and not(current_ips):
                logger.debug(f"There were not requests in the last {batch_minutes} minutes.")
                ip_predict_list = [start, end, [], []]
            
                return ip_predict_list
            else:
                # predict state
                predicted_ip_state = self.classifier.get_predictions(current_data_df)
            
                predicted_ip_state_list = predicted_ip_state.tolist()

                ip_predict_list = [start, end, current_ips, predicted_ip_state_list]

                logger.debug(f"IP state predicted: {'Normal' if predicted_ip_state[0] == 1 else 'Malicious'}")

                return ip_predict_list
    
        except Exception as e:
            logger.exception(f"Error predicting IP state: {str(e)}")
            return 