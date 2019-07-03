import base64
import json

from factories.url_factory import GSTURLFactory
from utils.fetch_utils import DataFetchBase
from transformers.list_returns_transformer import ListReturnsTransformer


from vayana_modules.exceptions import APIException


class ListReturns(DataFetchBase):

    URL_LABEL = "LIST_RETURNS"
    ACTION = "RETTRACK"

    def fetch(self, gstin, **kwargs):
        list_returns_url = GSTURLFactory.get_url(ListReturns.URL_LABEL, debug=self.debug)

        response = self.vayana_client.make_request(
            "GET",
            list_returns_url.format(
                gstin=gstin,
                fy=kwargs['fy']
            ),
            ListReturns.ACTION
        )

        if response.status_code != 200 or "error" in response.json():
            raise APIException(response.json()['error'])

        response_data = response.json()

        return response_data['data']

    def decrypt_and_decode(self, data):
        base64decoded = base64.b64decode(data)
        return json.loads(base64decoded)

    def transform(self, data):
        transformer = ListReturnsTransformer(data)
        return transformer.transform()
