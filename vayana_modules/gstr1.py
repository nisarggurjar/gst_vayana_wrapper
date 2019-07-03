import base64
import json

from factories.url_factory import GSTURLFactory
from utils.fetch_utils import DataFetchBase
from utils.encryption_utils import AESEncryption

from transformers.gstr1_summary_transformer import GSTR1SummaryTransformer

from vayana_modules.exceptions import APIException


class GSTR1Summary(DataFetchBase):

    URL_LABEL = "GSTR1_SUMMARY"
    ACTION = "RETSUM"

    def fetch(self, gstin, **kwargs):
        gstr1_summary_url = GSTURLFactory.get_url(GSTR1Summary.URL_LABEL, debug=self.debug)

        response = self.vayana_client.make_request(
            "GET",
            gstr1_summary_url.format(
                gstin=gstin,
                ret_period=kwargs['ret_period']
            ),
            GSTR1Summary.ACTION,
            addon_headers={
                "auth-token": kwargs['auth_token'],
                "ret_period": kwargs['ret_period'],
                "gstin": gstin,
                "username": kwargs['username']
            }
        )

        if response.status_code != 200 or "error" in response.json():
            raise APIException(response.json()['error'])

        response_data = response.json()

        return response_data

    def decrypt_and_decode(self, response_data, **kwargs):
        rek = AESEncryption.decrypt(kwargs['sek'], response_data['rek'])
        decoded_data = AESEncryption.decrypt(rek, response_data['data'])
        return json.loads(base64.b64decode(decoded_data))

    def transform(self, data):
        transformer = GSTR1SummaryTransformer(data)
        return transformer.transform()


class GSTR1(object):

    def __init__(
        self,
        gstin,
        gst_cust_id,
        gst_client_id,
        gst_client_secret,
        gsp_private_key,
        **kwargs
    ):

        self.gstr1_summary = GSTR1Summary(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key,
            **kwargs
        )