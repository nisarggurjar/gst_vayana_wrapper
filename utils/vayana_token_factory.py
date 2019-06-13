import uuid
from datetime import datetime


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
