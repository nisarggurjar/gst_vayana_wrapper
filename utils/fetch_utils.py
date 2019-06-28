from abc import ABCMeta, abstractmethod

from utils.vayana_client_base import VayanaRequest


class DataFetchBase(object):

    __metaclass__ = ABCMeta

    def __init__(
        self,
        gstin,
        gst_cust_id,
        gst_client_id,
        gst_client_secret,
        gsp_private_key,
        **kwargs
    ):
        self.debug = kwargs['debug']
        self.gstin = gstin
        self.gst_cust_id = gst_cust_id
        self.gst_client_id = gst_client_id
        self.gst_client_secret = gst_client_secret
        self.GST_PRIVATE_KEY = gsp_private_key

        self.vayana_client = VayanaRequest(
            gstin,
            gst_cust_id,
            gst_client_id,
            gst_client_secret,
            gsp_private_key
        )

    @abstractmethod
    def fetch(self, GSTIN, **kwargs):
        """
        Implement the method to fetch data from GST APIs
        """
        return

    @abstractmethod
    def decrypt_and_decode(self, data):
        """
        Implement the method to decrypt and decode from GST APIs
        """
        return

    @abstractmethod
    def transform(self, data):
        """
        Implement the method to adjust fetched data into a schema
        """
        return

    def fetch_decode_and_transform(self, GSTIN, **kwargs):

        response_data = self.fetch(GSTIN, **kwargs)
        decrypted_data = self.decrypt_and_decode(response_data)
        transformed_data = self.transform(decrypted_data)

        return transformed_data
