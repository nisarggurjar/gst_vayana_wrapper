import uuid
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_encrypt


class AppKey(object):

    def __init__(self, key, encrypted_key):
        self.encrypted_key = encrypted_key
        self.key = key


class AppKeyFactory(object):

    def __init__(self, gst_public_key):

        self.GST_PUBLIC_KEY = gst_public_key

    def get_app_key(self, app_key=None):

        if not app_key:
            app_key = uuid.uuid4().hex
        r_gst_public_key = RSA.importKey(self.GST_PUBLIC_KEY)
        cipher = PKCS1_v1_5_encrypt.new(r_gst_public_key)
        encrypted_app_key = cipher.encrypt(app_key)
        encrypted_app_key_base64 = base64.b64encode(encrypted_app_key)

        return AppKey(app_key, encrypted_app_key_base64)
