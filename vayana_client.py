from vayana_modules.auth import Auth


class VayanaClient(object):

    def __init__(self, gstin, gst_cust_id, gst_client_id, gst_private_key, gst_public_key):
        self.auth = Auth(gstin, gst_cust_id, gst_client_id, gst_private_key, gst_public_key)
