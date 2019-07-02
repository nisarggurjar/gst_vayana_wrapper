from vayana_modules.auth import Auth
from vayana_modules.health import Health
from vayana_modules.search import Search
from vayana_modules.list_returns import ListReturns


class VayanaClient(object):

    def __init__(
        self,
        gstin,
        gst_cust_id,
        gst_client_id,
        gst_client_secret,
        gsp_private_key,
        gst_public_key,
        **kwargs
    ):

        self.debug = True
        try:
            self.debug = kwargs['debug']
        except KeyError as e:
            pass

        self.auth = Auth(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key,
            gst_public_key,
            **kwargs
        )

        self.health = Health(debug=self.debug)

        self.search = Search(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key,
            **kwargs
        )

        self.list_returns = ListReturns(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key,
            **kwargs
        )
