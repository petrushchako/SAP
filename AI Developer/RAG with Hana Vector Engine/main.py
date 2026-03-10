dbutils.library.restartPython()

from hdbcli import dbapi
import hana_ml.dataframe as dataframe
from gen_ai_hub.proxy.langchain.openai import OpenAIEmbeddings
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain_community.vectorstores.hanavector import HanaDB


#############################################################################
###### This script is used to get the access token for the BTP LLM API ######
#############################################################################

import json
import requests

secret = dbutils.secrets.get(scope="PROD_XGTP_SCOPE", key="LEARNING_GENAIXL")
svcKey = json.loads(secret)
authUrl = svcKey["url"]
clientid = svcKey["clientid"]
clientsecret = svcKey["clientsecret"]
apiUrl = svcKey["serviceurls"]["AI_API_URL"]

# request token
params = {"grant_type": "client_credentials" }
resp = requests.post(f"{authUrl}/oauth/token",
                    auth=(clientid, clientsecret),
                    params=params)

BtpLlmApiUrl = apiUrl
BtpLlmAccessToken = resp.json()["access_token"]

# Set the environment variables for the BTP LLM API
import os 

# Define Keys HERE
env_vars = {    
 "AICORE_AUTH_URL": authUrl,
 "AICORE_CLIENT_ID": clientid,
 "AICORE_CLIENT_SECRET": clientsecret,
 "AICORE_RESOURCE_GROUP": "default",
 "AICORE_BASE_URL": apiUrl
}

os.environ.update(env_vars)
