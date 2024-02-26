from django.apps import apps
import logging
import datetime
from elasticsearch import exceptions
from anomaly_detection.constants import number_of_days, batch_minutes

logger = logging.getLogger(__name__)

def get_access_logs_by_date(date_str):
    """
    Get data of access logs from elastic index

    :param `str` date_str: The string of the date to retrieve daily data, in
        "YYYY.MM.DD" format

    :return `list` data_list: The content of the retrieved index
    """

    elastic_search_config = apps.get_app_config('elastic')

    elastic_connector = elastic_search_config.elastic_connector

    index = 'connectors-' + date_str
    
    try:
        data_list = elastic_connector.read_all_from_index(index)
    except exceptions.NotFoundError: 
        data_list = []

    if len(data_list) == 0:
        logger.error(f"The index connectors-{date_str} was not found.")
        return []
    
    return data_list

def get_access_logs_by_minutes(date_str, n):
    """
    Get data of access logs from elastic index

    :param `str` date_str: The string of the date to retrieve daily data, in
        "YYYY.MM.DD" format
    :param 'int' n: The number of previous minutes to extract the web logs

    :return `list` data_list: The document retrieved
    """

    logger.info('Get the connectors access logs')

    elastic_search_config = apps.get_app_config('elastic')

    elastic_connector = elastic_search_config.elastic_connector

    index = 'connectors-' + date_str

    query_pairs = [('@timestamp', {"gte": "now-{}m".format(n)})]
    query_keywords=[('filter', 'range')]
    
    try:
        data_list = elastic_connector.read_from_index(index, query_pairs, query_keywords)
    except exceptions.NotFoundError: 
        data_list = []

    if len(data_list) == 0:
        logger.error(f"The index connectors-{date_str} was not found.")
        return []
    
    return data_list

def list_to_dict(data_list):
    """
    Get data of access logs from elastic index

    :param `list` data_list: The list of the retrieved access logs

    :return `dict` data_dict: A dict in a form {index_of_access_log:contet_of_access_log}
    """

    logger.info('Convert the the list of the retrieved access logs to dictionary')

    data_dict = {}

    for index in enumerate(data_list):
        data_dict[index[0]] = data_list[index[0]].to_dict()

    return data_dict

def n_days_access_logs(number_of_days):
    """
    Get data of access logs from elastic index of the number_of_days previous days and
    stack them

    :param `int` number_of_days: The number of previous days to get the access logs

    :return `dict` data_dict: A dict in a form {index_of_access_log:contet_of_access_log}
    """

    logger.info('Stack the access logs of the previous {} days'.format(number_of_days))

    current_date = datetime.datetime.today()
    list_of_logs = []

    for i in range(number_of_days):

        previous_date = (current_date - datetime.timedelta(days=i+1)).strftime('%Y.%m.%d')

        list_of_logs.extend(get_access_logs_by_date(previous_date))

    data_dict = list_to_dict(list_of_logs)

    return data_dict

def n_minutes_access_logs(batch_minutes):
    """
    Get data of access logs from elastic index of the batch_minutes last minutes

    :param `int` batch_minutes: The number of last minutes to get the access logs

    :return `dict` data_dict: A dict in a form {index_of_access_log:contet_of_access_log}
    """

    current_date = datetime.datetime.today().strftime('%Y.%m.%d')

    list_of_logs = []

    list_of_logs = get_access_logs_by_minutes(current_date, batch_minutes)

    data_dict = list_to_dict(list_of_logs)

    return data_dict

def get_anomaly_detection_model():
    """
    Get data of anomaly detection model from elastic index

    :return `dict` data_dict: The content of the retrieved index
    """
    elastic_search_config = apps.get_app_config('elastic')

    elastic_connector = elastic_search_config.elastic_connector

    index = 'anomaly_detection_model'
    
    data_list = elastic_connector.read_all_from_index(index)

    if len(data_list) == 0:
        logger.error(f"The index {index} was not found.")
        return []
    
    data_dict = data_list[0].to_dict()

    return data_dict