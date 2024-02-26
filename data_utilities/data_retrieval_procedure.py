import logging
import pandas as pd
from elastic.utils import n_days_access_logs, n_minutes_access_logs
from anomaly_detection.utils import extract_features
from anomaly_detection.constants import number_of_days, batch_minutes

logger = logging.getLogger(__name__)

# Set the display option to show all columns
pd.set_option('display.max_columns', None)

def historic_data_retrieval_and_preparation(number_of_days):
    """
    Retrieve historic data for a period of number_of_days previous days
    and perform any processing during the dataframe preparation

    :param `int` number_of_days: The number of previous days to get the access logs

    :return `DataFrame` df_train: The dataframe to be used for training
    """

    data_dict = n_days_access_logs(number_of_days)

    if len(data_dict) == 0:

        df_train = pd.DataFrame()
        ips = []
        return df_train, ips

    else:

        data_df = pd.DataFrame.from_dict(data_dict, orient='index').reset_index()
    
        data_df['@timestamp'] = pd.to_datetime(data_df['@timestamp'], infer_datetime_format=True)
        data_df = data_df.set_index('@timestamp').sort_index()

        df_train, ips = extract_features(data_df, batch_minutes)

        return df_train, ips

def historic_data_retrieval_and_preparation_prediction(batch_minutes):
    """
    Retrieve historic data for a period of batch_minutes previous minutes
    and perform any processing during the dataframe preparation

    :param `int` batch_minutes: The number of previous minutes to get the access logs

    :return `DataFrame` df_train: The dataframe to be used for training
    """

    data_dict = n_minutes_access_logs(batch_minutes)
    
    if len(data_dict) == 0:
        
        df_predict = pd.DataFrame()
        ips = []
        return df_predict, ips
    
    else:

        data_df = pd.DataFrame.from_dict(data_dict, orient='index').reset_index()
    
        data_df['@timestamp'] = pd.to_datetime(data_df['@timestamp'], infer_datetime_format=True)
        data_df = data_df.set_index('@timestamp').sort_index()

        df_predict, ips = extract_features(data_df, batch_minutes)

        return df_predict, ips