import uuid
from datetime import datetime
from base64 import b64encode, b64decode
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_52


class VayanaToken(object):

    TOKEN_FORMAT = "v2.0:{gst_cust_id}:{gst_client_id}:{txn_id}:"\
                    "{timestamp}:{gstin}:{action}"

    def __init__(self, gstin, gst_cust_id, gst_client_id, action):

        self.GSTIN = gstin
        self.GST_CUST_ID = gst_cust_id
        self.GST_CLIENT_ID = gst_client_id
        self.action = action
        self.txn_id = uuid.uuid4().hex
        self.timestamp = datetime.today().strftime('%Y%m%d%H%M%S') + "+0530"

    def generate_signature(self, gst_private_key):

        rsa_key = RSA.importKey(gst_private_key)
        signer = PKCS1_v1_52.new(rsa_key)
        digest = SHA256.new()
        digest.update(b64decode(self.__str__()))
        sign = signer.sign(digest)
        return b64encode(sign)

    def __str__(self):

        return VayanaToken.TOKEN_FORMAT.format(
            gst_cust_id=self.GST_CUST_ID,
            gst_client_id=self.GST_CLIENT_ID,
            txn_id=self.txn_id,
            timestamp=self.timestamp,
            gstin=self.GSTIN,
            action=self.action
        )


class VayanaTokenFactory(object):

    def __init__(self, gstin, gst_cust_id, gst_client_id):

        self.GSTIN = gstin
        self.GST_CUST_ID = gst_cust_id
        self.GST_CLIENT_ID = gst_client_id

    def get_token(self, action):

        return VayanaToken(
            self.GSTIN,
            self.GST_CUST_ID,
            self.GST_CLIENT_ID,
            action
        )
