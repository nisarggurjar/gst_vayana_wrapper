from collections import OrderedDict
from transformers.transformer_base import TransformerBase


class TaxpayerInfoTransformer(TransformerBase):

    RENAME_DATA = OrderedDict([
        ("stjCd", "state_jurisdiction_code"),
        ("lgnm", "legal_name"),
        ("stj", "state_jurisdiction"),
        ("dty", "customer_type"),
        ("cxdt", "date_of_cancellation"),
        ("nba", "nature_of_business"),
        ("ctj", "centre_juristicton"),
        ("tradeNam", "trade_name"),
        ("adadr.addr.bnm", "building_name"),
        ("adadr.addr.st", "state"),
        ("adadr.addr.loc", "location"),
        ("adadr.addr.bno", "floor_number"),
        ("adadr.addr.lt", "latitude"),
        ("adadr.addr.lg", "longitude"),
        ("adadr.addr.pncd", "pincode"),
        ("adadr.addr", "address"),
        ("adadr.ntr", "nature_of_business"),
        ("adadr", "additional_place_of_business"),
        ("pradr.addr.bnm", "building_name"),
        ("pradr.addr.st", "state"),
        ("pradr.addr.loc", "location"),
        ("pradr.addr.bno", "floor_number"),
        ("pradr.addr.lt", "latitude"),
        ("pradr.addr.lg", "longitude"),
        ("pradr.addr.pncd", "pincode"),
        ("pradr.ntr", "nature_of_business"),
        ("pradr.addr", "address"),
        ("pradr", "principal_place_of_business")
    ])

    def rearrange_transformation(self):

        return self.data
