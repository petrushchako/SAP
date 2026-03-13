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



###############################################
###              Load PDF files             ###
###############################################

#Policy download links- https://one.int.sap/company/policies_and_guidelines/travel_and_mobility#procurement___travel_b9ff/sap_global_car_fleet_policy_

from langchain.document_loaders import PyPDFLoader

# Load PDF
loaders = [
    # Multiple documents on purpose - data
    PyPDFLoader("GlobalTravelPolicy (English).pdf"),
    PyPDFLoader("SAP Global Environmental Policy_Internal_ENGLISH.pdf"),
]
docs = []
for loader in loaders:
    docs.extend(loader.load())



###############################################
#####       Chunking with overlaps        #####
###############################################

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Modify the chunk_size and chunk_overlap parameters
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # You can change this value
    chunk_overlap=150  # You can change this value
)

splits = text_splitter.split_documents(docs)
len(splits)  # Output the number of chunks


###############################################
####           Create embeddings           ####
###############################################


from gen_ai_hub.proxy.native.openai import embeddings

response = embeddings.create(
    input="Non-compliance with the Global Travel Policy may lead to legal, tax or financial risk, and may even put SAP’s reputation at risk.",
    model_name="text-embedding-3-large"
)
print(response.data)
len(response.data[0].embedding)



embedding_model = OpenAIEmbeddings(proxy_model_name='text-embedding-3-large')
sentence1 = "The Global Travel Policy is based on SAP’s values, strategies, and principles"
sentence2 = "Do the cows come from Mars or from Vebus or from the lake nearby ?"
sentence3 = "SAP's Cloud Strategy is sound and customer adoption shows they value our company's offerings"

from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')
chat_llm = ChatOpenAI(proxy_model_name='gpt-4o-mini', proxy_client=proxy_client, temperature=0.0)

embedding1 = embedding_model.embed_query(sentence1)
embedding2 = embedding_model.embed_query(sentence2)
embedding3 = embedding_model.embed_query(sentence3)



##################################################################
####  Use NumPy to measure cosine similarity between vectors #####
##################################################################
import numpy as np
np.dot(embedding1, embedding2) # 0.04098079406732409
np.dot(embedding1, embedding2) # 0.4244397013593574
np.dot(embedding2, embedding3) # 0.04473057713577556





