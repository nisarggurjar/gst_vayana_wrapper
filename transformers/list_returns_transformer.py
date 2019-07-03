from collections import OrderedDict
from transformers.transformer_base import TransformerBase


class ListReturnsTransformer(TransformerBase):

    RENAME_DATA = OrderedDict([
        ("EFiledlist.ret_prd", "return_period"),
        ("EFiledlist.mof", "method_of_filing"),
        ("EFiledlist.dof", "date_of_filing"),
        ("EFiledlist.rtntype", "return_type"),
    ])

    def rearrange_transformation(self):
        self.data = self.data['EFiledlist']
