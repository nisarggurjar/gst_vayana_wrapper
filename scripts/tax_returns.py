import os
import logging
import argparse
from datetime import datetime
from vayana_client import VayanaClient
from pymongo import MongoClient

import local_settings as lc
from vayana_modules.exceptions import APIException

logger = logging.getLogger(__name__)


def get_arguments():

    arg_p = argparse.ArgumentParser()

    arg_p.add_argument(
        '--gstin', '-g',
        type=str,
        required=True,
        help='gstin belonging to the username'
    )
    arg_p.add_argument(
        '--username', '-u',
        type=str,
        required=True,
        help='username for which credentials are being passed'
    )
    arg_p.add_argument(
        '--app-key', '-ak',
        type=str,
        required=True,
        help='app key using which authtoken and sek was retrieved'
    )
    arg_p.add_argument(
        '--auth-token', '-at',
        type=str,
        required=True,
        help='auth token retrieved'
    )
    arg_p.add_argument(
        '--sek', '-sek',
        type=str,
        required=True,
        help='sek for the session'
    )

    return arg_p.parse_args()


def get_fy():

    year_counter = datetime.now().year + 1

    while year_counter > 2017:
        year_counter -= 1
        yield "{}-{}".format(year_counter, str(year_counter + 1)[2:])


if __name__ == "__main__":

    """
    This script is meant to pull all returns data for supplied credentials
    and push it to mongodb
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    m_conn = MongoClient()
    db = m_conn['gst_data']

    logging_handler = logging.FileHandler(os.path.join(BASE_DIR, "list_returns.log"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging_handler.setFormatter(formatter)
    logging_handler.setLevel(logging.INFO)
    logger.addHandler(logging_handler)
    logger.setLevel(logging.INFO)

    args = get_arguments()

    v_c = VayanaClient(
        lc.GSTN,
        "",
        lc.GST_CLIENT_ID,
        lc.GST_CLIENT_SECRET,
        lc.VAYANA_PRIVATE_KEY,
        lc.GST_PUBLIC_KEY,
        debug=False,
        ip_usr="35.154.52.160",
        state_cd=lc.GSTN[:2],
    )

    v_c.auth.preload_auth_params(
        args.username,
        args.app_key,
        args.auth_token,
        args.sek
    )

    returns_data = []
    for fy in get_fy():
        try:
            return_data = v_c.list_returns.fetch_decode_and_transform(args.gstin, fy=fy)
            for item in return_data:
                item['gstin'] = args.gstin

            returns_data += return_data
        except APIException as e:
            logger.info("Fetching return data for fy:{fy} failed due to {error}".format(
                fy=fy,
                error=e
            ))
            continue

        logger.info("Fetching return data for fy:{fy} succeeded".format(
            fy=fy
        ))

    db['returns_data'].delete_many({"gstin": args.gstin})
    db['returns_data'].insert_many(returns_data)
