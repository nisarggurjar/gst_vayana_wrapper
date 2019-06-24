from vayana_modules.auth import Auth
from vayana_modules.health import Health


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
            debug=self.debug
        )
        self.health = Health(debug=self.debug)
