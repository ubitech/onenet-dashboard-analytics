import logging
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

logger = logging.getLogger(__name__)


class ElasticSearchConnector():
    def __init__(self, nodes, **kwargs):
        '''
        The ElasticSearchConnector is used to perform requests to an ES node or cluster

        :param `list` nodes: The elastic nodes as full paths, e.g. ['localhost:9200']
        :param kwargs: Keyword arguments containing configuration of the Elasticsearch object
        '''
        self.es = Elasticsearch(nodes, **kwargs)

        if not self.es.ping():  # if ping is false then elastic is down
            raise ValueError("Connection with Elasticsearch failed")

    def create_index(self, index, params):
        '''
        Create and store the elastic index if it does not already exist.

        :param `str` index: The elastic index
        :param `dict` params: The parameters given in json format, regarding settings, mappings etc
        '''
        # check whether the index already exists, if not create it
        if not self.es.indices.exists(index):
            self.es.indices.create(index=index, ignore=400, body=params)

            logger.info("Created new index: {}".format(index))

    def read(self, index, query):
        '''
        Use in order to 'read' objects from ElasticSearch

        :param `str` index: The index of ElasticSearch that the application will read from
        :param `dict` query: The query to be used for searching, structured as json

        :return `list`: The resulted ElasticSearch Hits
        '''

        search = Search(using=self.es, index=index) \
            .update_from_dict(query)
        search.execute()

        logger.info(f'Searching in index {index} for {query}')
        return [s for s in search.scan()]

    def write(self, index, data):
        '''
        Use in order to 'write' objects to ElasticSearch
        :param `str` index: The elastic index
        :param `str` data: The payload with the actual data retrieved from Tiamat.

        '''
        res = self.es.index(index=index, body=data)
        # index will return insert info: like if created is True or False
        logger.debug(res)

