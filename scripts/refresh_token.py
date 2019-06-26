import json
import logging
import os
import sys

import local_settings
from vayana_client import VayanaClient
from vayana_modules.exceptions import VayanaAuthException

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    """
    This script is meant to be run in a cron to refresh token and avoid
    OTP authentication repeatedly
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    logging_handler = logging.FileHandler(os.path.join(BASE_DIR, "auth_data.log"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging_handler.setFormatter(formatter)
    logging_handler.setLevel(logging.INFO)
    logger.addHandler(logging_handler)
    logger.setLevel(logging.INFO)

    v_c = VayanaClient(
        local_settings.GSTN,
        "",
        local_settings.GST_CLIENT_ID,
        local_settings.GST_CLIENT_SECRET,
        local_settings.VAYANA_PRIVATE_KEY,
        local_settings.GST_PUBLIC_KEY,
        debug=False
    )

    data_file = open(os.path.join(BASE_DIR, "auth_data.json"), "r+")
    auth_data = json.loads(data_file.read())

    v_c.auth.preload_auth_params(
        str(auth_data['username']),
        str(auth_data['app_key']),
        str(auth_data['auth_token']),
        str(auth_data['sek'])
    )

    try:
        new_auth_data = v_c.auth.refresh_token(auth_data['username'])
    except VayanaAuthException as e:
        logger.info("Failed to refresh token" + str(e))
        sys.exit(1)

    new_auth_data['username'] = auth_data['username']
    new_auth_data['app_key'] = auth_data['app_key']
    del new_auth_data['status_cd']

    logger.info(json.dumps(new_auth_data))

    data_file.seek(0)
    data_file.truncate()
    data_file.write(json.dumps(new_auth_data))

    data_file.close()
    sys.exit(0)
