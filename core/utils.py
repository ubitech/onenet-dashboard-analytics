# Libraries
from django.core.exceptions import ImproperlyConfigured
from decouple import config, Csv

# Functions
def get_config(env_var: str, default=None, **kwargs):
    """
    Checks for type validity of cast function in the main config function.
    Thus, the faulty values will not be depicted from the configuration file.
    In case of incorrect cast type (casting bool to True1), an ImproperlyConfigured
    will be raised, denoting the cast and the variable.

    Examples: get_config('DEBUG', default='False', cast=bool)
              get_config('SECRET_KEY')

    For the keyword arguments,
    see documentation https://github.com/henriquebastos/python-decouple#usage.

    :param `str` env_var: The variable to be read from the configuration file
    :param `str` default: Default value of the env_var, if not given by the .env/environment
    :param kwargs: Keyword arguments. cast can be given as documented
    :return `object`: The configuration of the demanded variable

    Exceptions
    ----------
    @raise ImproperlyConfigured: raises an ImproperlyConfigured exception, in case of invalid cast type

    """
    try:
        return config(env_var, default=default, **kwargs)
    except ValueError:
        if default is None:
            error_msg = 'Variable {} is not present in the configuration'.format(
                env_var)
        else:
            error_msg = 'Demanded type of type cast "{}" for variable {} ' \
                'is invalid in the configuration'.format(
                    kwargs['cast'].__name__, env_var)
        raise ImproperlyConfigured(error_msg) from None


def to_list():
    """
    Cast a configuration variable to a list using the Csv() function from the decouple module.

    Example: ALLOWED_HOSTS = get_config('ALLOWED_HOSTS', '127.0.0.1, .localhost', cast=to_list())
    """
    return Csv()


def transform_dict_to_json_array_format(data: dict, labels: dict) -> dict:
    """
    Transform a dictionary of the given format {"key": "value"} to the json array format
    {"parent_label": [{"key_label": "key", "value_label": "value"}, ...]} 

    :param `dict` data: The dictionary containing the data
    :param `dict` labels: The dictionary containing the labels which must contain the 
        following keys: "parent" (the list's parent label), "key" (the data dict's key labels) 
        and "value" (the data dict's values label)

    :return `dict`: The transformed dictionary
    """
    formatted_data = []
    for key in data.keys():
        temp = {}
        temp[labels['key']] = key
        temp[labels['value']] = data[key]
        formatted_data.append(temp)
    return {labels['parent']: formatted_data}
