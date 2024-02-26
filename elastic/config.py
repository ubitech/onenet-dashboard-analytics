import logging
from django.apps import AppConfig
from core.utils import get_config, to_list
from elastic.elastic_connector import ElasticConnector

logger = logging.getLogger(__name__)


class ElasticSearchConfig(AppConfig):
    name = 'elastic'

    def _setup_elastic_configuration(self):
        '''
        Setup the Elasticsearch configuration by checking values inside the .env file
        '''
        config = {}
        auth_user = get_config('ELASTIC_USER')
        auth_pass = get_config('ELASTIC_PASS')
        if auth_user and auth_pass:
            config['http_auth'] = (auth_user, auth_pass)
        use_ssl = get_config('ELASTIC_SSL', False, cast=bool)
        ca_certs = get_config('ELASTIC_CERT_PATH')
        if use_ssl and ca_certs:
            config['scheme'] = 'https'
            config['use_ssl'] = use_ssl
            config['ca_certs'] = ca_certs
        return config

    def ready(self):
        config = self._setup_elastic_configuration()
        try:
            elastic_nodes = get_config(
                'ELASTIC_NODES',
                'http://localhost:9200',
                cast=to_list()
            )
            logger.debug(f"Elastic nodes read from env file {elastic_nodes}")

            self.elastic_connector = ElasticConnector(
                get_config(
                    'ELASTIC_NODES',
                    'http://localhost:9200',
                    cast=to_list()
                ),
                **config
            )

            self.elastic_status = 'up'
        except ValueError:
            logger.debug("Elasticsearch is not available")
            self.elastic_status = 'down'
