import logging
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

sts_host = ""
##Bos 申请获取AK
access_key_id = ""

##Bos 申请获取SK
secret_access_key = ""

logger = logging.getLogger('baidubce.services.sts.stsclient')
fh = logging.FileHandler("sample.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)

config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key), endpoint=sts_host)

