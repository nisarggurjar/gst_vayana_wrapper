import requests
from factories.vayana_token_factory import VayanaTokenFactory


class VayanaRequest(object):

    def __init__(self, gstin, gst_cust_id, gst_client_id, gst_client_secret, gsp_private_key, **kwargs):
        self.GSTIN = gstin
        self.GST_CUST_ID = gst_cust_id
        self.GST_CLIENT_ID = gst_client_id
        self.GST_CLIENT_SECRET = gst_client_secret
        self.GSP_PRIVATE_KEY = gsp_private_key
        self.ip_usr = kwargs['ip_usr']
        self.state_cd = kwargs['state_cd']

        self.token_factory = VayanaTokenFactory(
            gstin,
            gst_cust_id,
            gst_client_id,
            gsp_private_key
        )

    def make_request(self, method, base_url, action, payload=None, **kwargs):
        token = self.token_factory.get_token(action)

        headers = {
            "Content-Type": "application/json",
            "X-Asp-Auth-Token": str(token),
            "X-Asp-Auth-Signature": token.signature,
            "clientid": self.GST_CLIENT_ID,
            "client-secret": self.GST_CLIENT_SECRET,
            "ip-usr": self.ip_usr,
            "state-cd": self.state_cd,
            "txn": token.txn_id
        }

        if "addon_headers" in kwargs:
            headers.update(kwargs['addon_headers'])

        if not payload:
            return requests.request(
                method,
                base_url,
                headers=headers,
                timeout=5
            )

        return requests.request(
            method,
            base_url,
            headers=headers,
            json=payload,
            timeout=5
        )
