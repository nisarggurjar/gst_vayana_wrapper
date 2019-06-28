from requests.exceptions import ReadTimeout

from utils.vayana_client_base import VayanaRequest
from factories.app_key_factory import AppKeyFactory
from factories.url_factory import GSTURLFactory
from utils.encryption_utils import AESEncryption

from exceptions import VayanaAuthException


class Auth(object):

    MSG_AUTH_PARAMS_MISSING = "Auth param was not found. Authenticate or call preload_params."

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
            gsp_private_key,
            ip_usr=kwargs['ip_usr'],
            state_cd=kwargs['state_cd']
        )

    def reset_auth_params(self):
        '''
        reset auth params
        '''

        self.__app_key = None
        self.__authtoken = None
        self.__sek = None
        self.__username = None

    def preload_auth_params(self, username, app_key, authtoken, sek):
        '''
        app_key object
        GST authtoken
        sek decrypted
        '''

        app_key_factory = AppKeyFactory(self.GST_PUBLIC_KEY)
        app_key_obj = app_key_factory.get_app_key(app_key)

        self.__app_key = app_key_obj
        self.__authtoken = authtoken
        self.__sek = AESEncryption.decrypt(self.__app_key.key, sek)
        self.__username = username

    def request_otp(self, username):
        self.reset_auth_params()

        app_key_factory = AppKeyFactory(self.GST_PUBLIC_KEY)
        app_key = app_key_factory.get_app_key()

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)
        payload = {
            "action": "OTPREQUEST",
            "app_key": app_key.encrypted_key,
            "username": username
        }

        try:
            response = self.vayana_client.make_request(
                auth_url,
                "OTPREQUEST",
                payload
            )
        except ReadTimeout as e:
            raise VayanaAuthException(e)

        response_data = response.json()

        if("error" in response_data and response_data['error']):
            raise VayanaAuthException(response_data['error'])

        if(response_data['status_cd'] == '1'):
            self.__app_key = app_key

        return response_data

    def get_authtoken(self, username, otp):

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)

        payload = {
            "action": "AUTHTOKEN",
            "username": username,
            "app_key": self.__app_key.encrypted_key,
            "otp": AESEncryption.encrypt(self.__app_key.key, otp)
        }

        try:
            response = self.vayana_client.make_request(
                auth_url,
                "AUTHTOKEN",
                payload
            )
        except ReadTimeout as e:
            raise VayanaAuthException(e)

        response_data = response.json()

        if("error" in response_data and response_data['error']):
            raise VayanaAuthException(response_data['error'])

        if(response_data['status_cd'] == '1'):
            self.__authtoken = response_data['auth_token']
            self.__sek = AESEncryption.decrypt(
                self.__app_key.key,
                response_data['sek']
            )
            self.__username = username

        return response_data

    def refresh_token(self, username):

        auth_url = GSTURLFactory.get_url("AUTH", debug=self.debug)

        sek_encrypted_app_key = AESEncryption.encrypt(self.__sek, self.__app_key.key)

        payload = {
            "action": "REFRESHTOKEN",
            "username": username,
            "app_key": sek_encrypted_app_key,
            "auth_token": self.__authtoken
        }

        try:
            response = self.vayana_client.make_request(
                auth_url,
                "REFRESHTOKEN",
                payload
            )
        except ReadTimeout as e:
            raise VayanaAuthException(e)

        response_data = response.json()

        if("error" in response_data and response_data['error']):
            raise VayanaAuthException(response_data['error'])

        if(response_data['status_cd'] == '1'):
            self.__authtoken = response_data['auth_token']
            self.__sek = AESEncryption.decrypt(
                self.__app_key.key,
                response_data['sek']
            )
            self.__username = username

        return response_data

    def authtoken(self):

        try:
            return self.__authtoken
        except AttributeError as e:
            raise VayanaAuthException(Auth.MSG_AUTH_PARAMS_MISSING)

    def app_key(self):

        try:
            return self.__app_key
        except AttributeError as e:
            raise VayanaAuthException(Auth.MSG_AUTH_PARAMS_MISSING)

    def sek(self):

        try:
            return self.__sek
        except AttributeError as e:
            raise VayanaAuthException(Auth.MSG_AUTH_PARAMS_MISSING)

    def username(self):

        try:
            return self.__username
        except AttributeError as e:
            raise VayanaAuthException(Auth.MSG_AUTH_PARAMS_MISSING)
