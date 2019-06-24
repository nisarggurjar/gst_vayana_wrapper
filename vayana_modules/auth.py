from utils.vayana_client_base import VayanaRequest
from factories.app_key_factory import AppKeyFactory
from factories.url_factory import GSTURLFactory


class Auth(object):

    def __init__(self, gstin, gst_cust_id, gst_client_id, gst_private_key, gst_public_key, **kwargs):
        self.debug = kwargs['debug']
        self.gstin = gstin
        self.gst_cust_id = gst_cust_id
        self.gst_client_id = gst_client_id
        self.gst_private_key = gst_private_key
        self.gst_public_key = gst_public_key

        self.vayana_client = VayanaRequest(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_private_key
        )

    def request_otp(self, username, app_key):
        app_key = AppKeyFactory(self.gst_public_key)

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)
        payload = {
            "action": "OTPREQUEST",
            "app_key": app_key.encrypted_key,
            "username": username
        }

        return self.vayana_client.make_request(
            auth_url,
            "OTPREQUEST",
            payload
        )
