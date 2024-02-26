import pandas as pd
import datetime
import logging

logger = logging.getLogger(__name__)

def chunk(df, delta_in_min):
    """
    Create batches with duration delta_in_min containing access logs
    
    :param `DataFrame` df: The dataframe to split in chunks (index is based on datetimes)
    :param `int` delta_in_min: The size of chunk in minute (at least one).
    
    :return `DataFrame` df: The Chunk of input dataframe of the given size
    """

    logger.info('Starting the creation of batches of the access logs')

    start = df.index[0]
    while True:
        if delta_in_min <= 0:
            yield df
            break
        end = start + pd.Timedelta(value=delta_in_min, unit="m")
        if end > df.index[-1]:
            yield df.loc[(df.index >= start), :]
            break
        yield df.loc[(df.index >= start) & (df.index < end), :]
        start = end
        if start > df.index[-1]:
            break

def extract_features(df, batch_minutes):
    """
    Extract the features to be used by anomaly detection algorithm
    
    :param `DataFrame` df: The dataframe to split in chunks (index is based on datetimes)
    :param `int` batch_minutes: The size of chunk in minute (at least one).
    
    :return `DataFrame` df_final: The dataframe to be used for training/prediction
    """

    logger.info('Starting the extraction of features of the batches of the access logs')

   # Extract 'name' from 'user_agent' column
    df['user_agent_name'] = df['user_agent'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)

    df_final = []
    ips = []

    for batch in chunk(df, batch_minutes):
        unique_ips = batch.groupby('client_ip')['client_ip'].unique()
        unique_request = batch.groupby('client_ip')['client_ip'].count()
        unique_ua = batch.groupby('client_ip')['user_agent_name'].nunique()
        reply_length_avg = batch.groupby('client_ip')['bytes'].mean()
        response4xx = batch.groupby('client_ip')['response'].apply(lambda x: x.astype(str).str.startswith('4').sum())
        concat = pd.concat([unique_request, unique_ua, reply_length_avg, response4xx], axis = 1, ignore_index = True)
        df_final.append(concat)
        ips.append(unique_ips.index.tolist()) # append the indexes of the unique_ips DataFrame, which represent the unique IPs in the batch

    df_final = pd.concat(df_final, axis = 0, ignore_index = True)
    # ips = pd.concat(ips, axis = 0, ignore_index = True)
    ips = [x for x in ips if x] # remove all the empty lists
    ips = [item for sublist in ips for item in sublist] # flatten the list
    
    return df_final, ips

def convert_dict_for_serializer(input):
    """ 
    Take the predictions in the form [timestamp_from, timestamp_to, current_ips_list, predicted_ip_state_list] and convert it to a proper form for the serializer.

    :param `list` input: The list with the prediction data from the prediction job

    :return `dict` output: The dictionary with the transformed form
    """ 

    prefix = ["timestamp_from", "timestamp_to", "ip", "ip_status"]

    output = dict(zip(prefix, input))

    return output

def predictions_to_frontend(input):

    """ 
    Take result from the query of the predictions and convert it to proper form for the frontend.

    :param `dict` input: The dictionary as it comes from the serializer
    
    :return `list` output: The output in the proper form for the frontend
    """ 
    
    output = []

    for i in range(len(input)):    
    
        temp = {}
        temp["timestamp_from"] = datetime.datetime.strptime(input[i]["timestamp_from"], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%Y-%m-%d %H:%M")
        temp["ip"] = input[i]["ip"]
        temp["ip_status"] = input[i]["ip_status"]

        output.append(temp)
    
    return output