import requests

################################################################################
class Requests:
    HTTP_OK         = 200
    HTTP_CREATED    = 201
    HTTP_ACEPTED    = 202

    HTTP_METHOD_GET = 'GET'
    HTTP_METHOD_POST= 'POST'

    class Error(Exception):
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    class HttpError(Error):
        def __init__(self, status_code):
            Requests.Error.__init__(self)
            self.__status_code = status_code

        def __str__(self):
            return "Http error. Code '%d'." % self.__status_code

    def __init__(self, client):
        self.__client                   = client
        self.__session                  = None

    def make_http_error(self, status_code):
        return self.HttpError(status_code)

    def session(self):
        if not self.__session:
            self.__session = requests.Session()
        return self.__session

    def client(self):
        return self.__client

    def get2(self, query, **kwargs):
        """
            HTTP get. Uncached version.
        """
        kwargs['headers'] = self.client().headers()
        return self.session().get(query, **kwargs)

    def post2(self, query, data, **kwargs):
        """
            HTTP post. Uncached version.
        """
        kwargs['headers'] = self.client().headers()
        kwargs['data'] = data
        return self.session().post(query, **kwargs)

    def put2(self, query, **kwargs):
        """
            HTTP put. Uncached version.
        """
        kwargs['headers'] = self.client().headers()
        r = self.session().put(query, **kwargs)
        if r.status_code not in [ self.HTTP_OK, self.HTTP_CREATED, self.HTTP_ACEPTED ]:
            raise self.make_http_error(r.status_code)
        return r
