import base64
import json

from factories.url_factory import GSTURLFactory
from utils.fetch_utils import DataFetchBase
from utils.encryption_utils import AESEncryption

from transformers.gstr1_summary_transformer import GSTR1SummaryTransformer

from vayana_modules.exceptions import APIException


class GSTRFetch(DataFetchBase):

    TRANSFORMER_MAP = {
        "GSTR1": {
            "RETSUM": GSTR1SummaryTransformer,
        }
    }

    def fetch(self, gstin, **kwargs):
        gstr1_summary_url = GSTURLFactory.get_url(
            kwargs['return_type'],
            debug=self.debug
        )

        response = self.vayana_client.make_request(
            "GET",
            gstr1_summary_url.format(
                gstin=gstin,
                ret_period=kwargs['ret_period'],
                action=kwargs['invoice_type'],
                return_type=kwargs['return_type'].lower()
            ),
            kwargs['invoice_type'],
            addon_headers={
                "auth-token": kwargs['auth_token'],
                "ret_period": kwargs['ret_period'],
                "gstin": gstin,
                "username": kwargs['username']
            },
            timeout=10
        )

        if response.status_code != 200 or "error" in response.json():
            raise APIException(response.json()['error'])

        response_data = response.json()

        return response_data

    def decrypt_and_decode(self, response_data, **kwargs):
        rek = AESEncryption.decrypt(kwargs['sek'], response_data['rek'])
        decoded_data = AESEncryption.decrypt(rek, response_data['data'])
        return json.loads(base64.b64decode(decoded_data))

    def transform(self, data, **kwargs):

        try:
            transformer = GSTRFetch.TRANSFORMER_MAP[kwargs['return_type']][kwargs['invoice_type']]
        except KeyError:
            return data

        transformer = GSTR1SummaryTransformer(data)
        return transformer.transform()


class GSTR(object):

    def __init__(
        self,
        gstin,
        gst_cust_id,
        gst_client_id,
        gst_client_secret,
        gsp_private_key,
        **kwargs
    ):

        self.gstr_fetch = GSTRFetch(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key,
            **kwargs
        )
