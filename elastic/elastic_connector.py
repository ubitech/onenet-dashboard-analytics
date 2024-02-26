import logging
from core.generic_elastic_connector import ElasticSearchConnector

logger = logging.getLogger(__name__)


class ElasticConnector(ElasticSearchConnector):
    """
    Elastic Connector is responsible for providing basic read, writing, creating etc index functions
    based on the abstract class Elastic Search Connector
    """

    def __init__(self, nodes, **kwargs):
        super().__init__(nodes, **kwargs)
        logger.info('ElasticConnector has been initialized')

    def check_index_existence(self, index):
        """
        Checking if an index exists

        :param `str` index: The index name

        :return `bool`: True if index exists, False otherwise
        """
        return self.es.indices.exists(index)

    def create_index(self, index, mapping=None):
        """
        Creating an index by providing an index name and a prefered mapping,
        otherwise the fields will be mapped dynamically

        :param `str` index: The index name
        :param `dict` mapping: A mapping for the new index
        """
        params = {
            "settings": {"number_of_replicas": 0}
        }

        if mapping:
            params.update(mapping)

        return super().create_index(index, params)

    def read_from_index(self, index, query_pairs, query_keywords):
        """
        Reading from an index by forming and executing a query

        :param `str` index: The index name
        :param `list` query_pairs: The field-value pairs of the query given as a list
            of tuples in the form (field, value) i.e. [('id', building_id), ('zone_id', area_id)]
        :param `list` query_keywords: A list of the query keyword pairs in tuples, respective to each query pair,
            where the first kw is an elastic query parameter (must, must_not, filter) and the second kw is the leaf
            query kw (match, term, range), i.e. [('must', 'match'), ('filter', 'term')]

        :return `list`: The list of resulted ElasticSearch Hits
        """

        query = self._form_query(query_pairs, query_keywords)

        return super().read(index=index, query=query)
    
    def read_all_from_index(self, index):
        
        query = {'query': {'match_all': {}}}

        return super().read(index=index, query=query)

    def write_to_index(self, index, data):
        """
        Writing a document to elastic index

        :param `str` index: The index name
        :param `dict` data: The data in dictionary (json) format to write in index
        """
        return super().write(index, data)

    def _form_query(self, query_pairs, query_keywords):
        '''
        Form a boolean query with each value pair and the respective query keywords. For each query 
        parameter there can be more than one leaf queries. 

        :param `list` query_pairs: The field-value pairs of the query given as a list
            of tuples in the form (field, value) i.e. [('id', building_id), ('zone_id', area_id)]
        :param `list` query_keywords: A list of the query keyword tuples, respective to each query pair,
            where the first kw is a query parameter (one of: must, must_not, filter) and the second kw is the leaf
            query kw (one of: match, term, range), i.e. [('must', 'match'), ('filter', 'term')]

        :return `dict`: The query formatted
        '''
        query = {'query': {'bool': {}}}

        must_queries, must_not_queries, filter_queries = \
            self._add_leaf_queries(query_pairs, query_keywords)

        query = self._add_query_param(query, 'must', must_queries)
        query = self._add_query_param(query, 'must_not', must_not_queries)
        query = self._add_query_param(query, 'filter', filter_queries)

        return query

    def _add_leaf_queries(self, query_pairs, query_keywords):
        """
        Adding leaf queries for each query parameter. A leaf query is formed as a dictionary with
        key the leaf query keyword and value the field-value pair again as dictionary.

        :param `list` query_pairs: The field-value pairs of the query given as a list
            of tuples in the form (field, value) i.e. [('id', building_id), ('zone_id', area_id)]
        :param `list` query_keywords: A list of the query keyword tuples, respective to each query pair,
            where the first kw is a query parameter (one of: must, must_not, filter) and the second kw is the leaf
            query kw (one of: match, term, range), i.e. [('must', 'match'), ('filter', 'term')]

        :return `list` must_queries: The list of leaf queries for 'must' query parameter
        :return `list` must_not_queries: The list of leaf queries for 'must_not' query parameter
        :return `list` filter_queries: The list of leaf queries for 'filter' query parameter
        """
        
        must_queries = []
        must_not_queries = []
        filter_queries = []

        # field, value = pair, so pair[0]=field, pair[1]=value
        for pair, kws in zip(query_pairs, query_keywords):
            if kws[0] == 'must':
                must_queries.append({kws[1]: {pair[0]: pair[1]}})
            if kws[0] == 'must_not':
                must_not_queries.append({kws[1]: {pair[0]: pair[1]}})
            if kws[0] == 'filter':
                filter_queries.append({kws[1]: {pair[0]: pair[1]}})

        return must_queries, must_not_queries, filter_queries

    def _add_query_param(self, query, keyword, query_list):
        '''
        Adding a query parameter to the query dictionary, along with its list of leaf queries

        :param `dict` query: The query that will be enriched
        :param `str` keyword: The keyword of the query parameter (possible values: 'must', 'must_not', 'filter')
        :param `list` query_list: The list of the leaf queries to be added to the query

        :return `dict`: The query enriched
        '''
        if len(query_list) > 0:
            query['query']['bool'][keyword] = query_list

        return query
