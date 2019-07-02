from collections import OrderedDict
from transformers.transformer_base import TransformerBase


class TaxpayerInfoTransformer(TransformerBase):

    RENAME_DATA = OrderedDict([
        ("ret_prd", "return_period"),
        ("mof", "method_of_filing"),
        ("dof", "date_of_filing"),
        ("rtntype", "return_type"),
    ])

    def rearrange_transformation(self):
        return self.data['EFiledlist']
