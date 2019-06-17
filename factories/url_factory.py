class GSTURLFactory(object):

    BASE_URL_PRODUCTION = "https://api.gsp.vayana.com/gus"
    BASE_URL_STAGING = "https://yoda.api.vayanagsp.in/gus"

    URL_MAPPINGS = {
        "AUTH": "/taxpayerapi/v1.0/authenticate/"
    }

    @staticmethod
    def get_url(label, **kwargs):

        if(kwargs['debug']):
            base_url = BASE_URL_STAGING
        else:
            base_url = BASE_URL_PRODUCTION

        return "{base_url}{predicate}".format(
            base=base_url,
            predicate=GSTURLFactory.URL_MAPPINGS[label]
        )
