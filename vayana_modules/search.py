from utils.fetch_utils import DataFetchBase


class Search(DataFetchBase):

    URL_LABEL = "SEARCH"
    ACTION = "TP"

    def fetch(self, GSTIN, **kwargs):
        pass

    def decrypt_and_decode(self, data):
        pass

    def transform(self, data):
        pass
