class GSTURLFactory(object):

    BASE_URL_PRODUCTION = "https://api.gsp.vayana.com/gus"
    BASE_URL_STAGING = "https://yoda.api.vayanagsp.in/gus"

    URL_MAPPINGS = {
        "AUTH": "/taxpayerapi/v1.0/authenticate",
        "HEALTH": "/gstn-health/main",
        "SEARCH": "commonapi/v1.1/search?action=TP&gstin={gstin}"
    }

    @staticmethod
    def get_url(label, **kwargs):

        return "{base_url}{predicate}".format(
            base_url=GSTURLFactory.get_base_url(**kwargs),
            predicate=GSTURLFactory.URL_MAPPINGS[label]
        )

    @staticmethod
    def get_base_url(**kwargs):

        if(kwargs['debug']):
            base_url = GSTURLFactory.BASE_URL_STAGING
        else:
            base_url = GSTURLFactory.BASE_URL_PRODUCTION

        return base_url
