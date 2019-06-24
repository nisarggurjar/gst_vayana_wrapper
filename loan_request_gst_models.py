from __future__ import unicode_literals
from bson.objectid import ObjectId
from mongoengine import Document, EmbeddedDocument, fields
import datetime
from bson import json_util
import traceback
from Utils import logging

class LoanRequestGstDetails(Document):
	loan_request_id = fields.ObjectIdField(required=True)
	gstin = fields.StringField()
	username = fields.StringField(required=True)
	state_cd = fields.StringField()
	created_at = fields.DateTimeField()
	updated_at = fields.DateTimeField(default=datetime.datetime.now)


	@classmethod
	def save(self, *args, **kwargs):
		if not self.creation_date:
			self.creation_date = datetime.datetime.now()
		self.updated_date = datetime.datetime.now()
		return super(LoanRequestGstDetails, self).modify(*args, **kwargs)


	def find_and_update_loan_request_gst_details(self, find_query, update_data, upsert=False):
		data = {}
		try:
			payload = {}
			payload['set__loan_request_id'] = ObjectId(update_data["loan_request_id"])
			payload['set__gstin'] = update_data["gstin"]
			payload['set__username'] = update_data["username"]
			payload['set__state_cd'] = update_data['state_cd']
			loan_request_gst_details_object = LoanRequestGstDetails.objects(**find_query).modify(upsert=upsert, new= True, **payload)
			data = loan_request_gst_details_object.id

		except Exception as e:
			logging.log_exception(
		            e,
		            data=json_util.dumps({}),
		            tracebacklog=traceback,
		            modes=['file', 'mailalert'],
		            subject='GST MODELS - Updating GST details'
		        )
		return data


	def get_loan_request_gst_details_object(self, **kwargs):
		find_query = {}
		data = None

		if 'loan_request_id' in kwargs:
			find_query['loan_request_id'] = kwargs.get('loan_request_id')

		try:
			data = LoanRequestGstDetails.objects.get(**find_query)
		except Exception as e:
			pass
		return data

	

class LoanRequestGstAuth(Document):
	loan_request_gst_details_id = fields.ObjectIdField(required=True)
	app_key = fields.StringField(required=True)
	encrypted_app_key = fields.StringField(required=True)
	action = fields.StringField(required=True)
	timestamp = fields.StringField()
	otp = fields.StringField()
	fetched_auth_token = fields.StringField()
	expiry = fields.StringField()
	sek = fields.StringField()
	created_at = fields.DateTimeField()
	updated_at = fields.DateTimeField(default=datetime.datetime.now)
	loan_request_gst_payload_id = fields.ObjectIdField()


	@classmethod
	def save(self, *args, **kwargs):
		if not self.created_at:
			self.created_at = datetime.datetime.now()
		self.updated_at = datetime.datetime.now()
		return super(LoanRequestGstAuth, self).save(*args, **kwargs)


	def find_and_update_loan_request_gst_auth(self, find_query, update_data, upsert=False):

		payload = {}

		if 'loan_request_gst_details_id' in update_data:
			loan_request_gst_details_id = update_data.get('loan_request_gst_details_id')

		if 'app_key' in update_data:
			payload['set__app_key'] = update_data.get('app_key')

		if 'encrypted_app_key' in update_data:
			payload['set__encrypted_app_key'] = update_data.get('encrypted_app_key')

		if 'timestamp' in update_data:
			payload['set__timestamp'] = update_data.get('timestamp')

		if 'action' in update_data:
			payload['set__action'] = update_data.get('action')

		if 'otp' in update_data:
			payload['set__otp'] = update_data.get('otp')

		if 'fetched_auth_token' in update_data:
			payload['set__fetched_auth_token'] = update_data.get('fetched_auth_token')

		if 'expiry' in update_data:
			payload['set__expiry'] = update_data.get('expiry')

		if 'sek' in update_data:
			payload['set__sek'] = update_data.get('sek')

		if 'loan_request_gst_payload_id' in update_data:
			payload['set__loan_request_gst_payload_id'] = update_data.get('loan_request_gst_payload_id')

		loan_request_gst_auth_object = LoanRequestGstAuth.objects(**find_query).modify(upsert=upsert, new= True, **payload)

		return loan_request_gst_auth_object

		


	def get_loan_request_gst_auth_object(self, **kwargs):
		data = None
		if 'loan_request_gst_details_id' in kwargs:
			try:
				data = LoanRequestGstAuth.objects.get(loan_request_gst_details_id = kwargs.get('loan_request_gst_details_id'))
			except Exception as e:
				pass
		return data



class SecSumCptySum(EmbeddedDocument):
	meta = {'allow_inheritance': True}
	chksum = fields.StringField()
	ttl_rec = fields.IntField()
	ttl_val = fields.FloatField()
	ttl_igst = fields.FloatField()
	ttl_sgst = fields.FloatField()
	ttl_cgst = fields.FloatField()
	ttl_cess = fields.FloatField()
	ttl_tax = fields.FloatField()

class CptySum(SecSumCptySum):
	ctin = fields.StringField()


class SecSum(SecSumCptySum):
	sec_nm = fields.StringField()
	ttl_doc_issued = fields.IntField()
	net_doc_issued = fields.IntField()
	ttl_doc_cancelled = fields.IntField()
	ttl_expt_amt = fields.FloatField()
	ttl_ngsup_amt = fields.FloatField()
	ttl_nilsup_amt = fields.FloatField()
	cpty_sum = fields.ListField(fields.EmbeddedDocumentField(CptySum))


class Gstr1SummaryData(EmbeddedDocument):
	ret_period = fields.StringField()
	chksum = fields.StringField()
	summ_typ = fields.StringField()
	sec_sum = fields.ListField(fields.EmbeddedDocumentField(SecSum))


class LoanRequestGstReturn1Summary(Document):
	loan_request_gst_details_id = fields.ObjectIdField(required=True)
	rek = fields.StringField()
	hmac = fields.StringField()
	data = fields.EmbeddedDocumentField(Gstr1SummaryData)
	loan_request_gst_payload_id = fields.ObjectIdField()
	created_date = fields.DateTimeField()
	updated_date = fields.DateTimeField(default = datetime.datetime.now)


	def find_and_update_loan_request_gst_return1_summary(self, loan_request_gst_details_id=None, rek=None, hmac=None, data=None, created_at=datetime.datetime.now(), updated_at=datetime.datetime.now(), loan_request_gst_payload_id=None):
		result = None
		try:
			ret_period = data.get('ret_period')
			chksum = data.get('chksum')
			summ_typ = data.get('summ_typ')
			sec_sum = data.get('sec_sum')
			gstr1_data_object = Gstr1SummaryData(ret_period=ret_period, chksum=chksum, summ_typ=summ_typ, sec_sum=sec_sum)
			result = LoanRequestGstReturn1Summary(loan_request_gst_details_id=loan_request_gst_details_id, rek=rek, hmac=hmac, data=gstr1_data_object, loan_request_gst_payload_id=loan_request_gst_payload_id).save()
		except Exception as e:
			logging.log_exception(
		            e,
		            data=json_util.dumps({}),
		            tracebacklog=traceback,
		            modes=['file', 'mailalert'],
		            subject='GST MODELS - Updating GST Return 1 Summary'
		        )

		return result


	def get_loan_request_gst_return1_summary(self, **kwargs):
		data = None
		find_query = {}
		if 'loan_request_gst_details_id' in kwargs:
			find_query['loan_request_gst_details_id'] = kwargs.get('loan_request_gst_details_id')

		try:
			data = LoanRequestGstReturn1Summary.objects.get(**find_query)
		except Exception as e:
			pass

		return data


class Payload(EmbeddedDocument):
	request = fields.DictField()
	response = fields.DictField()
	headers = fields.DictField()


class LoanRequestGstPayload(Document):
	payload = fields.ListField(fields.EmbeddedDocumentField(Payload))
	created_at = fields.DateTimeField()
	updated_at = fields.DateTimeField(default=datetime.datetime.now)

	def get_loan_request_gst_payload(self, **kwargs):
		data = None
		find_query = {}
		if 'loan_request_gst_payload_id' in kwargs:
			find_query['id'] = kwargs.get('loan_request_gst_payload_id')

		try:
			data = LoanRequestGstPayload.objects.get(**find_query)
		except Exception as e:
			pass

		return data

	def find_and_update_loan_request_gst_payload(self, loan_request_gst_payload_id, request_payload, response_payload, headers):
		data = None
		loan_request_gst_payload_object = LoanRequestGstPayload()
		loan_request_gst_payload_object = loan_request_gst_payload_object.get_loan_request_gst_payload(loan_request_gst_payload_id=loan_request_gst_payload_id)

		payload_data = Payload(request=request_payload, response=response_payload, headers=headers)

		if loan_request_gst_payload_object:
			payload = loan_request_gst_payload_object.payload
			payload.append(payload_data)
		else:
			loan_request_gst_payload_object = LoanRequestGstPayload(payload=[payload_data])

		try:
			data = loan_request_gst_payload_object.save()
		except Exception as e:
			pass

		return data
