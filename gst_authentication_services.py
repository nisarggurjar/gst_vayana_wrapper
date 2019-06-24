from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import random
import string
import datetime
import base64
import hashlib
from Crypto import Random
from ziploan.keys import GST_AUTHENTICATE_URL, GST_ZIPLOAN_PRIVATE_KEY, GST_PUBLIC_KEY, GST_PUBLIC_IP, GST_CLIENT_ID, GST_CLIENT_SECRET, GST_CUST_ID, GST_RETURN1_URL
import requests
import json
from ziploan_next.common.models.loan_request_gst_models import LoanRequestGstDetails, LoanRequestGstAuth, LoanRequestGstReturn1Summary, SecSum, CptySum, LoanRequestGstPayload
from ziploan_next.common.models.loan_request_models import LoanRequest
from ziploan_next.application_sourcing.models.loan_request_business_info_model import LoanRequestBusinessInfo
from ziploan_next.common.services.utils import AESCipher
import os
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_51
from Crypto.Signature import PKCS1_v1_5 as PKCS1_v1_52
import io
from bson import ObjectId, json_util
import uuid
from Utils import logging
import traceback

def get_state_code(state_name):
	state_name = state_name.replace(' ','_').strip().lower()
	state_codes = {
		'jammu_&_kashmir' :' 01',
		'himachal_pradesh' : '02',
		'punjab' : '03',
		'chandigarh' : '04',
		'uttarakhand' : '05',
		'haryana' : '06',
		'delhi' : '07',
		'rajasthan' : '08',
		'uttar_pradesh' : '09',
		'bihar' : '10',
		'sikkim' : '11',
		'arunachal_pradesh' : '12',
		'nagaland' : '13',
		'manipur' : '14',
		'mizoram' : '15',
		'tripura' : '16',
		'meghalaya' : '17',
		'assam' : '18,',
		'west_bengal' : '19',
		'jharkhand' : '20',
		'orissa' : '21',
		'chhattisgarh' : '22',
		'madhya_pradesh' : '23',
		'gujarat' : '24',
		'daman_&_diu' : '25',
		'dadra_&_nagar haveli' : '26',
		'maharashtra' : '27',
		'andhra_pradesh' : '28',
		'karnataka' : '29',
		'goa' : '30',
		'lakshadweep' : '31',
		'kerala' : '32',
		'tamil_nadu' : '33',
		'puducherry' : '34',
		'andaman_&_nicobar islands' : '35',
		'telengana' : '36',
		'andrapradesh(new)' : '37',
	}

	state_code = state_codes.get(state_name)

	if state_code:
		state_code = str(state_code)

	return state_code


def get_business_state(loan_request_id):
	loan_request_business_details_object = LoanRequestBusinessInfo()
	loan_request_business_details = loan_request_business_details_object.get_business_object(loan_request_id = loan_request_id)
	business_state = None
	if loan_request_business_details:
		business_state = loan_request_business_details.business_state
	else:
		raise Exception('Business details found for loan-application-number :' + str(loan_application_number))
	return str(business_state)


def generate_transaction_id():
	return random.randint(10000000, 99999999)


def generate_auth_token(gstin, action):
	txn_id = str(generate_transaction_id())
	timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S') + "+0530"
	data = "v2.0" + ":" + GST_CUST_ID + ":" + GST_CLIENT_ID + ":" + txn_id + ":" + timestamp + ":" + gstin + ":" + action
	return data, txn_id, timestamp


def generate_auth_signature(private_key_loc, data):

	key = open(private_key_loc, "r").read()
	rsakey = RSA.importKey(key)
	signer = PKCS1_v1_52.new(rsakey)
	digest = SHA256.new()
	digest.update(b64decode(data))
	sign = signer.sign(digest)
	return b64encode(sign)


def generate_app_key():
	app_key = uuid.uuid4().hex
	r_pkey = RSA.importKey(open(GST_PUBLIC_KEY))
	cipher = PKCS1_v1_51.new(r_pkey)
	X = cipher.encrypt(app_key)
	return app_key, base64.b64encode(X)

def pad(s):
	bs = 16
	return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

def encrypt_otp(otp, app_key=None):
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(app_key, AES.MODE_ECB, iv)
	return base64.urlsafe_b64encode(cipher.encrypt(pad(otp)))


def initiate_authenticate_gst(loan_application_number, gstin, username):
	action = 'OTPREQUEST'
	try:
		auth_token_tuple = generate_auth_token(gstin, action)
		generated_auth_token = str(auth_token_tuple[0])
		txn_id = str(auth_token_tuple[1])
		timestamp = str(auth_token_tuple[2])
		auth_signature = str(generate_auth_signature(GST_ZIPLOAN_PRIVATE_KEY, b64encode(generated_auth_token)))
		app_key_tuple = generate_app_key()
		app_key = app_key_tuple[0]
		encrypted_app_key = app_key_tuple[1]

		loan_request_object = LoanRequest()
		loan_request_object = loan_request_object.get_loan_request(loan_application_number=loan_application_number)
		loan_request_id = loan_request_object.id

		business_state = get_business_state(loan_request_id=loan_request_id)
		if not business_state:
			raise Exception('State not found in business details for : ' + str(loan_application_number))

		state_cd = get_state_code(business_state)

		if not state_cd:
			raise Exception('State Code not found for loan-application-number : ' + str(loan_application_number) + ' and state : ' + str(business_state))

		update_data = {
						"loan_request_id": loan_request_id,
						"gstin":gstin,
						"username": username,
						"state_cd": state_cd
						}

		gst_details_object = LoanRequestGstDetails()
		loan_request_gst_details_id = gst_details_object.find_and_update_loan_request_gst_details({"loan_request_id": loan_request_id}, update_data, upsert=True)

		if not loan_request_gst_details_id:
			raise Exception('Error while saving GST details corresponding to application number : ' + str(loan_application_number))

		headers = {
					"clientid":GST_CLIENT_ID,
					"client-secret": GST_CLIENT_SECRET,
					"state-cd": state_cd,
					"ip-usr": GST_PUBLIC_IP,
					"txn": txn_id,
					"X-Asp-Auth-Token": generated_auth_token,
					"X-Asp-Auth-Signature": auth_signature
					}

		request_payload = {"action": action, "app_key": encrypted_app_key, "username": username}
		response_payload = json.loads((requests.post(GST_AUTHENTICATE_URL, json = request_payload, headers = headers)).content)
		response = response_payload
		if str(response.get('status_cd')) != '1':
			raise Exception('OTP Generation failed, GST server issue')


		loan_request_gst_auth_object = LoanRequestGstAuth()
		loan_request_gst_auth_object = loan_request_gst_auth_object.get_loan_request_gst_auth_object(loan_request_gst_details_id = loan_request_gst_details_id)

		if loan_request_gst_auth_object:
			loan_request_gst_payload_id = loan_request_gst_auth_object.loan_request_gst_payload_id
		else:
			loan_request_gst_payload_id = None

		loan_request_gst_payload_object = LoanRequestGstPayload()
		loan_request_gst_payload_object = loan_request_gst_payload_object.find_and_update_loan_request_gst_payload(loan_request_gst_payload_id=loan_request_gst_payload_id, request_payload=request_payload, response_payload=response_payload, headers=headers)

		if not loan_request_gst_payload_object:
			raise Exception('Error while saving Gst Payloads corresponding to application number : ' + str(loan_application_number))

		loan_request_gst_payload_id = loan_request_gst_payload_object.id

		find_query = {
					'loan_request_gst_details_id': str(loan_request_gst_details_id)
					}

		update_data = {
					'loan_request_gst_details_id': str(loan_request_gst_details_id),
					'app_key' : app_key,
					'encrypted_app_key' : encrypted_app_key,
					'action' : action,
					'timestamp': timestamp,
					'loan_request_gst_payload_id' : ObjectId(loan_request_gst_payload_id)
				}

		loan_request_gst_auth_object = LoanRequestGstAuth()
		loan_request_gst_auth_object = loan_request_gst_auth_object.find_and_update_loan_request_gst_auth(find_query, update_data, upsert=True)

		if not loan_request_gst_auth_object:
			raise Exception('Error while saving Initiate Authentication details corresponding to application number : ' + str(loan_application_number))

	except Exception as e:
		logging.log_exception(
		            e,
		            data=json_util.dumps({}),
		            tracebacklog=traceback,
		            modes=['file', 'mailalert'],
		            subject='GST Services - Intitiate Auth Request'
		        )

	return response


def verify_authenticate_gst(loan_application_number, otp):

	try:
		if loan_application_number is None or otp is None:
			return {'error':'Missing loan-application-number or OTP'}

		action = 'AUTHTOKEN'

		loan_request_object = LoanRequest()
		loan_request_object = loan_request_object.get_loan_request(loan_application_number = loan_application_number)
		loan_request_id = loan_request_object.id
		loan_request_gst_details_object = LoanRequestGstDetails()
		loan_request_gst_details_object = loan_request_gst_details_object.get_loan_request_gst_details_object(loan_request_id=loan_request_id)
		state_cd = loan_request_gst_details_object.state_cd

		if loan_request_gst_details_object:
			loan_request_gst_details_id = loan_request_gst_details_object.id
			username = loan_request_gst_details_object.username
			gstin = loan_request_gst_details_object.gstin

		loan_request_gst_auth_object = LoanRequestGstAuth()
		loan_request_gst_auth_object = loan_request_gst_auth_object.get_loan_request_gst_auth_object(loan_request_gst_details_id=ObjectId(loan_request_gst_details_id))

		if loan_request_gst_auth_object:
			last_action = loan_request_gst_auth_object.action
			updated_at = loan_request_gst_auth_object.updated_at
			app_key = loan_request_gst_auth_object.app_key
			encrypted_app_key = loan_request_gst_auth_object.encrypted_app_key
			expiry = loan_request_gst_auth_object.expiry
			loan_request_gst_payload_id = loan_request_gst_auth_object.loan_request_gst_payload_id

		current_time = datetime.datetime.now()

		if last_action != 'OTPREQUEST' and int(expiry) < int((current_time - updated_at).seconds):
			response = {'success':'Session or token expired'}

		elif last_action == 'OTPREQUEST':
			app_key = app_key
			encrypted_app_key = encrypted_app_key
			auth_token_tuple = generate_auth_token(gstin,action)
			timestamp = auth_token_tuple[2]
			txn_id = auth_token_tuple[1]
			generated_auth_token = auth_token_tuple[0]
			auth_signature = generate_auth_signature(GST_ZIPLOAN_PRIVATE_KEY, b64encode(generated_auth_token))

			request = {
					'action': action,
					'username': username,
					'app_key': encrypted_app_key,
					'otp':encrypt_otp(otp, app_key)
				   }

			headers = {'clientid':GST_CLIENT_ID, 'client-secret':GST_CLIENT_SECRET, 'txn': txn_id, 'X-Asp-Auth-Signature': auth_signature, 'ip-usr': GST_PUBLIC_IP, 'state-cd': state_cd, 'X-Asp-Auth-Token': generated_auth_token}
			response = json.loads((requests.post(GST_AUTHENTICATE_URL, json = request, headers = headers)).content)


			loan_request_gst_payload_object = LoanRequestGstPayload()
			loan_request_gst_payload_object = loan_request_gst_payload_object.find_and_update_loan_request_gst_payload(loan_request_gst_payload_id=loan_request_gst_payload_id, request_payload=request, response_payload=response, headers=headers)

			if not loan_request_gst_payload_object:
				raise Exception('Error while saving AUTHTOKEN Gst Payload corresponding to application number : ' + str(loan_application_number))


		response_status = response.get('status_cd')
		if str(response_status) == '0':
			response = {'error': 'Invalid session'}
		else:
			fetched_auth_token = response.get('auth_token')
			sek = str(response.get('sek'))
			expiry = str(response.get('expiry'))
			loan_request_gst_payload_id = loan_request_gst_payload_object.id
			find_query = {'loan_request_gst_details_id':loan_request_gst_details_id}
			update_data = {
							'fetched_auth_token':fetched_auth_token,
							'sek': sek,
							'expiry' : expiry,
							'loan_request_gst_payload_id' : ObjectId(loan_request_gst_payload_id)
							}
			updated_loan_request_gst_auth_object = loan_request_gst_auth_object.find_and_update_loan_request_gst_auth(find_query, update_data)
			if not updated_loan_request_gst_auth_object:
				raise Exception('Error while saving Initiate authentication response corresponding to application number : ' + str(loan_application_number))

	except Exception as e:
		logging.log_exception(
	            e,
	            data=json_util.dumps({}),
	            tracebacklog=traceback,
	            modes=['file', 'mailalert'],
	            subject='GST Services - Verify Authenticate/OTP'
	        )

	return response


def refresh_token_gst():
	action = 'REFRESHTOKEN'
	loan_request_object = LoanRequest()
	loan_request_object = loan_request_object.get_loan_request(loan_application_number = loan_application_number)
	loan_request_id = loan_request_object.id

	headers = {
				"state-cd": "33",
				"ip-usr": public_ip,
				"txn": txn_id,
				"X-Asp-Auth-Token": auth_token,
				"X-Asp-Auth-Signature": auth_signature
				}

	data = {
			"username":username,
			"app_key":"ydHc7CA7s0pL/RplEzKZO4Ge4b9i0nMV+5tGXk36u6bzMH/RMr4nPpEV+7M7SBh0e3semIdDVJultpr++44ovWd8e4VQ+TFwkBVD3LZX2LFlPa55tjmy+eyDPj7n3bMCyDeiUI96fveJ89CK8c9AmCmAjuHMvLTOTDobRSYZ/FkLs7Lrsq81H/AJFnJPnYc6khxp1agXI+p/ttzmnDFTb5BgDkZS5Xwhk1H9xgD5pp0MK+Ncsjt/4lU6biuJHXlIM4LoZZHd4mWNzA5Eza0lOz7R3lJeBqJhBf5zVqUIISZyEAnAJDZFkrpkRg5z6REeUqPvJ4Hv+vNrDq5jdo66DQ==",
			"action":action,
			"auth_token":"f095e1caecb34ca1b506f3df0603a393"
			}

	response = json.loads((requests.post(GST_AUTHENTICATE_URL, json = data, headers= headers)).content)


def search_taxpayer(loan_application_number):
	try:
		action = 'TP'
		loan_request_object = LoanRequest()
		loan_request_object = get_loan_request(loan_application_number = loan_application_number)
		if not loan_request_object:
			raise Exception('Loan Request not found corresponding to : ' + str(loan_application_number))

		loan_request_id = loan_request_object.id
		loan_request_gst_details_object = LoanRequestGstDetails()
		loan_request_gst_details_object = loan_request_gst_details_object.get_loan_request_gst_details_object(loan_request_id = loan_request_id)

		if loan_request_gst_details_object:
			gstin = loan_request_gst_details_object.gstin
			state_cd = loan_request_gst_details_object.state_cd
			username = loan_request_gst_details_object.username
			loan_request_gst_details_id = loan_request_gst_details_object.id

			loan_request_gst_auth_object = LoanRequestGstAuth()
			loan_request_gst_auth_object = loan_request_gst_auth_object.get_loan_request_gst_auth_object(loan_request_gst_details_id = loan_request_gst_details_id)
			if loan_request_gst_auth_object:
				fetched_auth_token = loan_request_gst_auth_object.fetched_auth_token

		auth_token_tuple = generate_auth_token(gstin,action)
		txn_id = auth_token_tuple[1]
		auth_token = auth_token_tuple[0]
		auth_signature = generate_auth_signature(GST_ZIPLOAN_PRIVATE_KEY, b64encode(auth_token))
		headers = {
					"clientid" : GST_CLIENT_ID,
					"client-secret" : GST_CLIENT_SECRET,
					"state-cd": state_cd,
					"ip-usr": GST_PUBLIC_IP,
					"txn": txn_id,
					"X-Asp-Auth-Token": auth_token,
					"X-Asp-Auth-Signature": auth_signature
					}

		search_taxpayer_api_url = "https://api.gsp.vayana.com/gus/commonapi/v1.1/search?action={action}&gstin={gstin}".format(action=action,gstin=gstin)
		response = json.loads((requests.get(search_taxpayer_api_url, headers=headers)).content)
	except Exception as e:
		logging.log_exception(
		            e,
		            data=json_util.dumps({}),
		            tracebacklog=traceback,
		            modes=['file', 'mailalert'],
		            subject='GST Services - Search Taxpayer'
		        )

	return


def decrypt_return_data(app_key, sek, rek, data):

	SekDecrypter = AESCipher(app_key)
	decrypted_sek = SekDecrypter.decrypt(sek)
	decrypted_sek = base64.b64decode(base64.b64encode(decrypted_sek))
	RekDecrypter = AESCipher(decrypted_sek)
	decrypted_rek = RekDecrypter.decrypt(rek)
	DataDecrypter = AESCipher(decrypted_rek)
	decrypted_data = DataDecrypter.decrypt(data)
	json_data = base64.b64decode(decrypted_data)
	return json_data



def gstr1_summary(loan_application_number, ret_period):

	try:
		if loan_application_number is None or ret_period is None:
			raise Exception('Loan application number or return period not provided')

		loan_request_object = LoanRequest()
		loan_request_object = loan_request_object.get_loan_request(loan_application_number = loan_application_number)

		if not loan_request_object:
			raise Exception('Loan request not found corresponding to application number : ' + str(loan_application_number))

		loan_request_id = loan_request_object.id
		loan_request_gst_details_object = LoanRequestGstDetails()
		loan_request_gst_details_object = loan_request_gst_details_object.get_loan_request_gst_details_object(loan_request_id = loan_request_id)

		if not loan_request_gst_details_object:
			raise Exception('GST details not found corresponding to application number : ' + str(loan_application_number))

		gstin = loan_request_gst_details_object.gstin
		username = loan_request_gst_details_object.username
		state_cd = loan_request_gst_details_object.state_cd

		loan_request_gst_details_id = loan_request_gst_details_object.id

		loan_request_gst_auth_object = LoanRequestGstAuth()
		loan_request_gst_auth_object = loan_request_gst_auth_object.get_loan_request_gst_auth_object(loan_request_gst_details_id = loan_request_gst_details_id)

		if not loan_request_gst_auth_object:
			raise Exception('GST auth details not found corresponding to application number : ' + str(loan_application_number))

		fetched_auth_token = loan_request_gst_auth_object.fetched_auth_token
		app_key = loan_request_gst_auth_object.app_key
		action = 'RETSUM'
		auth_token_tuple = generate_auth_token(gstin,action)
		txn_id = auth_token_tuple[1]
		auth_token = auth_token_tuple[0]
		timestamp = auth_token_tuple[2]
		auth_signature = generate_auth_signature(GST_ZIPLOAN_PRIVATE_KEY, b64encode(auth_token))
		headers = {
					"clientid" : GST_CLIENT_ID,
					"client-secret" : GST_CLIENT_SECRET,
					"state-cd": state_cd,
					"ip-usr": GST_PUBLIC_IP,
					"txn": txn_id,
					"X-Asp-Auth-Token": auth_token,
					"X-Asp-Auth-Signature": auth_signature,
					"gstin":gstin,
					"username":username,
					"auth-token": fetched_auth_token,
					"ret_period": ret_period
					}

		url = GST_RETURN1_URL + '?action={action}&gstin={gstin}&ret_period={ret_period}'.format(gstin=gstin,ret_period=ret_period,action=action)
		response = json.loads((requests.get(url, headers=headers)).content)
		data = response.get('data')
		rek = str(response.get('rek'))
		hmac = str(response.get('hmac'))
		sek = loan_request_gst_auth_object.sek
		json_data = decrypt_return_data(app_key, sek, rek, data)
		json_data = json.loads(json_data)

		loan_request_gst_return1_summary_object = LoanRequestGstReturn1Summary()
		loan_request_gst_return1_summary_object = loan_request_gst_return1_summary_object.get_loan_request_gst_return1_summary(loan_request_gst_details_id=loan_request_gst_details_id)

		if loan_request_gst_return1_summary_object:
			loan_request_gst_payload_id = loan_request_gst_return1_summary_object.loan_request_gst_payload_id
		else:
			loan_request_gst_payload_id = None

		loan_request_gst_payload_object = LoanRequestGstPayload()
		loan_request_gst_payload_object = loan_request_gst_payload_object.find_and_update_loan_request_gst_payload(loan_request_gst_payload_id=loan_request_gst_payload_id, request_payload={'GET':url}, response_payload=response, headers=headers)

		if loan_request_gst_payload_object:
			loan_request_gst_payload_id = loan_request_gst_payload_object.id

		loan_request_gst_return1_summary_object = LoanRequestGstReturn1Summary()
		loan_request_gst_return1_summary_object = loan_request_gst_return1_summary_object.find_and_update_loan_request_gst_return1_summary(loan_request_gst_details_id=loan_request_gst_details_id, rek=rek, hmac=hmac, data=json_data, loan_request_gst_payload_id=loan_request_gst_payload_id)

		if loan_request_gst_return1_summary_object:
			response = {'loan-application-number': loan_application_number, 'GSTR1-Summary': json.dumps(json_data)}
		else:
			response = {'loan-application-number': 'Error while saving data'}

	except Exception as e:
		logging.log_exception(
		            e,
		            data=json_util.dumps({}),
		            tracebacklog=traceback,
		            modes=['file', 'mailalert'],
		            subject='GST Services - Gst return 1 summary'
		        )
	return response
