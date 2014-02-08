# This script is used to delete blobs older than one day. This script
# can be used as a webjob on an Azure site.

from datetime import datetime, timedelta
import time
import socket
import logging
import os

from azure.storage import *

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    config = {
        "account_name"    : "ping13",
        "container"       : "send2geoadmin",
    }
    config['url'] = "http://%s.blob.core.windows.net/%s" % (config['account_name'], config['container'])
    # get the storage access key from an environmant variable
    # (This can be set in Azure's management portal)
    try:
        config['access_key'] = os.environ['APPSETTING_storage_access_key']
    except:
        logging.error("Whoops, there is no storage key defined")
        raise 
    blob_service = BlobService(account_name= config['account_name'], 
                               account_key=  config['access_key'])

    blobs = blob_service.list_blobs(config['container'], include = "metadata")
    logging.info("found %d blobs." % len(blobs))
    now_dt  = datetime.utcnow()
    for blob in blobs:
        # example value for blob.properties.last_modified:
        # "Sat, 08 Feb 2014 10:39:50 GMT"
        blob_dt = datetime.strptime(blob.properties.last_modified, 
                                    '%a, %d %b %Y %H:%M:%S %Z')
        if (now_dt - blob_dt) > timedelta (days = 1):
            try:
                blob_service.delete_blob(config['container'], blob.name)
            except socket.error:
                logging.warn("couldn't delete %s" % blob.name)
                time.sleep(10)
            time.sleep(1)
        else:
            logging.info("keeping %s: %s" % (blob.name, blob_dt))


