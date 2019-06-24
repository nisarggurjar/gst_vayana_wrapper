import base64
from Crypto.Cipher import AES
from Crypto import Random

from utils.vayana_client_base import VayanaRequest
from factories.app_key_factory import AppKeyFactory
from factories.url_factory import GSTURLFactory

from exceptions import VayanaAuthException


class Auth(object):

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
        self.debug = kwargs['debug']
        self.gstin = gstin
        self.gst_cust_id = gst_cust_id
        self.gst_client_id = gst_client_id
        self.gst_client_secret = gst_client_secret
        self.GST_PRIVATE_KEY = gsp_private_key
        self.GST_PUBLIC_KEY = gst_public_key

        self.vayana_client = VayanaRequest(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key
        )

    def preload_auth_params(self, username, app_key, authtoken, sek):
        '''
        app_key object
        GST authtoken
        sek decrypted
        '''

        self.app_key = app_key
        self.authtoken = authtoken
        self.sek = sek
        self.username = username

    def request_otp(self, username):
        app_key_factory = AppKeyFactory(self.GST_PUBLIC_KEY)
        app_key = app_key_factory.get_app_key()

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)
        payload = {
            "action": "OTPREQUEST",
            "app_key": app_key.encrypted_key,
            "username": username
        }

        response = self.vayana_client.make_request(
            auth_url,
            "OTPREQUEST",
            payload
        )

        response_data = response.json()

        if("error" in response_data and response_data['error']):
            raise VayanaAuthException(response_data['error'])

        if(response_data['status_cd'] == 1):
            self.app_key = app_key

        return response_data

    def get_authtoken(self, username, otp):

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)

        payload = {
            "action": "AUTHTOKEN",
            "username": username,
            "app_key": self.app_key,
            "otp": self._encrypt_otp(otp)
        }

        response = self.vayana_client.make_request(
            auth_url,
            "AUTHTOKEN",
            payload
        )

        response_data = response.json()

        if(response_data['status_cd'] == 1):
            self.authtoken = response_data['auth_token']
            self.sek = self._decrypt_sek(response_data['sek'])

        return response_data

    def _encrypt_otp(self, otp):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.app_key, AES.MODE_ECB, iv)

        padded_otp = self.pad(otp)
        encrypted_otp = cipher.encrypt(padded_otp)
        return base64.urlsafe_b64encode(encrypted_otp)

    def _pad(self, otp):
        '''
        pad the otp with a block size of 16
        '''
        bs = 16
        return otp + (bs - len(otp) % bs) * chr(bs - len(otp) % bs)

    def _decrypt_sek(self, sek_base64_encoded):
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.app_key, AES.MODE_ECB, iv)
        return cipher.decrypt(base64.b64decode(sek_base64_encoded))
