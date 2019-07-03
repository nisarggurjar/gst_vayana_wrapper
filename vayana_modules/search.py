import base64
import json

from factories.url_factory import GSTURLFactory
from utils.fetch_utils import DataFetchBase
from transformers.taxpayer_info_transformer import TaxpayerInfoTransformer

from vayana_modules.exceptions import APIException


class Search(DataFetchBase):

    URL_LABEL = "SEARCH"
    ACTION = "TP"

    def fetch(self, gstin, **kwargs):
        search_url = GSTURLFactory.get_url(Search.URL_LABEL, debug=self.debug)

        response = self.vayana_client.make_request(
            "GET",
            search_url.format(gstin=gstin),
            Search.ACTION
        )

        if response.status_code != 200 or "error" in response.json():
            raise APIException(response.json()['error'])

        response_data = response.json()

        return response_data['data']

    def decrypt_and_decode(self, data, **kwargs):
        base64decoded = base64.b64decode(data)
        return json.loads(base64decoded)

    def transform(self, data, **kwargs):
        transformer = TaxpayerInfoTransformer(data)
        return transformer.transform()
