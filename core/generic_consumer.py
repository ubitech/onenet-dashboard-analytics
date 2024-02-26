import abc
from abc import ABC, abstractmethod
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError
import logging
from .api_response_model import APIResponseModel
from rest_framework import status

logger = logging.getLogger(__name__)


class GenericConsumer(ABC):
    @abstractmethod
    def __init__(self, call_timeout=10):
        """
        The GenericConsumer performs requests using the 'requests' Python module to a given web server

        :param `int` call_timeout: Set how much time at max a call should be waited before completing (in seconds)
        """
        self.call_timeout = call_timeout

    @abstractmethod
    def form_base_url(self, server, force_ssl=False):
        '''
        Generate the base url of the endpoint

        :param `str` server: The server name/IP
        :param `int` port: The port number
        :param `bool` force_ssl: Whether to force SSL to the request by using 'https://' over 'http://' (default)

        :return `str`: The base url of the endpoint
        '''
        base_url = 'http://'
        if force_ssl:
            base_url = 'https://'
        base_url += server + '/'
        return base_url

    @abstractmethod
    def perform_get_request(self, url, params, headers):
        """
        Performs a `GET` request to the specified url

        :param `str` url: The url to request
        :param `dict` params: The parameters passed
        :param `dict` headers: The headers passed

        :return `json`: The response content
        """
        try:
            logger.info(
                f'Performing HTTP Get Request | URL: {url} - Parameters: {params}'
            )
            response = requests.get(
                url, params=params, headers=headers, timeout=self.call_timeout)
            response.raise_for_status()
            response_body = None
            if len(response.text) > 0:
                response_body = response.json()
            response_model = APIResponseModel(
                response.status_code, response.headers, response_body)
        except Timeout:
            logger.error(
                f'Request Timed Out | URL: {url} - Parameters: {params}'
            )
            response_model = APIResponseModel(
                status=status.HTTP_504_GATEWAY_TIMEOUT, error='Request Timed Out')
        except ConnectionError:
            logger.error(
                f'Connection to {url} failed, is the web server up and running?'
            )
            response_model = APIResponseModel(
                status=status.HTTP_502_BAD_GATEWAY, error=f'Connection to {url} failed'
            )
        except HTTPError:
            logger.error(
                f'An HTTP error occurred while trying to reach {url}'
            )
            response_model = APIResponseModel(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, error='An HTTP error occurred')
        return response_model
