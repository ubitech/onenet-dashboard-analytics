class APIResponseModel:
    def __init__(self, status=None, headers=None, data=None, error=None):
        """
        The APIResponseModel serves as a unified model that will present the API response of a request

        :param `int` status: The request status code
        :param `json` headers: The full headers `json` object
        :param `json` data: The request's response body
        :param `str` error: The error returned when an error occurs
        """
        self.status = status
        self.headers = headers
        self.data = data
        self.error = error

    def __str__(self):
        return (
            f'APIResponseModel("status": {str(self.status)}, '
            f'"headers": {str(self.headers)}, "data": {str(self.data)}, '
            f'"error": {str(self.error)})'
        )
