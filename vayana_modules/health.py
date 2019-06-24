import requests
from factories.url_factory import GSTURLFactory


class Health(object):

    def __init__(self, **kwargs):

        self.debug = kwargs['debug']

    def ping(self):

        url = GSTURLFactory.get_url("HEALTH", debug=self.debug)
        return {
            "url": url,
            "status": requests.get(url).text
        }
