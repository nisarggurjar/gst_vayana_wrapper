from collections import OrderedDict
from transformers.transformer_base import TransformerBase


class GSTR1SummaryTransformer(TransformerBase):

    RENAME_DATA = OrderedDict([
        ("ret_period", "return_period"),
        ("gstin", "business_gstin"),
        ("sec_sum.ttl_igst", "total_igst"),
        ("sec_sum.ttl_cgst", "total_cgst"),
        ("sec_sum.ttl_sgst", "total_sgst"),
        ("sec_sum.ttl_val", "total_value"),
        ("sec_sum.ttl_tax", "total_tax"),
        ("sec_sum.ttl_rec", "total_invoices_issued"),
        ("sec_sum.ttl_cess", "total_cess"),
        ("sec_sum.sec_nm", "type"),
        ("sec_sum.cpty_sum.ctin", "gstin"),
        ("sec_sum.cpty_sum.ttl_igst", "total_igst"),
        ("sec_sum.cpty_sum.ttl_cgst", "total_cgst"),
        ("sec_sum.cpty_sum.ttl_sgst", "total_sgst"),
        ("sec_sum.cpty_sum.ttl_val", "total_value"),
        ("sec_sum.cpty_sum.ttl_tax", "total_tax"),
        ("sec_sum.cpty_sum.ttl_rec", "total_invoices_issued"),
        ("sec_sum.cpty_sum.ttl_cess", "total_cess"),
        ("sec_sum.cpty_sum", "buyer_info"),
        ("sec_sum", "summary_sections"),
    ])

    DEL_DATA = [
        "chksum",
        "sec_sum.chksum",
        "sec_sum.cpty_sum.chksum",
    ]

    def rearrange_transformation(self):
        for section in self.data['summary_sections']:

            if section['type'] != "DOC_ISSUE":
                continue

            self.data['total_invoices_issed'] = section['ttl_doc_issued']
            self.data['total_invoices_cancelled'] = section['ttl_doc_cancelled']
            self.data['net_invoices_issued'] = section['net_doc_issued']

            del section
