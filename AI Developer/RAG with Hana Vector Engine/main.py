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



#############################################################################
######                           Load PDF files                        ######
#############################################################################

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



#############################################################################
#####                       Chunking with overlaps                      #####
#############################################################################

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Modify the chunk_size and chunk_overlap parameters
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # You can change this value
    chunk_overlap=150  # You can change this value
)

splits = text_splitter.split_documents(docs)
len(splits)  # Output the number of chunks


#############################################################################
######                         Create embeddings                       ######
#############################################################################


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



#############################################################################
######      Use NumPy to measure cosine similarity between vectors     ######
#############################################################################
import numpy as np
np.dot(embedding1, embedding2) # 0.04098079406732409
np.dot(embedding1, embedding2) # 0.4244397013593574
np.dot(embedding2, embedding3) # 0.04473057713577556



#############################################################################
######                   Load vectors into HANA DB                     ######
#############################################################################
# Define the HANA Cloud username (most probably DBADMIN)
HANA_USER_VDB = 'DBADMIN'

# Define the HANA Cloud password (replace by the value you defined during the HANA Cloud instance creation)
HANA_PASSWORD_VDB = '***************'

# Define the HANA Cloud host - this host was configured during the HANA Cloud instance creation
# Hint1- This is your SQL Endpoint. But remove ":443" from the SQL Endpoint as port is already hardcoded
# Hint2- In HANA Cloud Central, click on your instance, then click on button "Copy SQL Endpoint" at the top right corner

HANA_HOST = '***************************.hana.trial-us10.hanacloud.ondemand.com'


# Use connection settings
connection = dbapi.connect(
    address=HANA_HOST,
    port=443,
    user=HANA_USER_VDB,
    password=HANA_PASSWORD_VDB,
    encrypt='true',
    autocommit=True
)

# Connection Context
conn = dataframe.ConnectionContext(
    address=HANA_HOST,  
    port=443,
    user=HANA_USER_VDB,
    password=HANA_PASSWORD_VDB,
    encrypt='true',
    autocommit=True
)
print(conn)



from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client

proxy_client = get_proxy_client('gen-ai-hub')
chat_llm = ChatOpenAI(proxy_model_name='gpt-4o-mini', proxy_client=proxy_client, temperature=0.0)

db = HanaDB(
    embedding=embedding_model,
    connection=connection,
    table_name="TRAVEL_AND_ENVIRONMENT_POLICY"
    # vector_column_length=1536
)

# Delete already existing documents from the table
db.delete(filter={})

# add the loaded document chunks 
db.add_documents(splits)


# take a look at the table
hdf = conn.sql(''' SELECT "VEC_TEXT", "VEC_META", TO_NVARCHAR("VEC_VECTOR") AS "VEC_VECTOR" FROM "TRAVEL_AND_ENVIRONMENT_POLICY" ''')
df = hdf.head(10).collect()
df


retriever = db.as_retriever()



#############################################################################
######                   Building the RAG Pipeline                     ######
#############################################################################

from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("""Provide answers based on context provided:

<context>
{context}
</context>

Question: {input}""")


from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

document_chain = create_stuff_documents_chain(chat_llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)


response = retrieval_chain.invoke({"input": "Which are the certified environmental and energy management systems that SAP run?"})
print(response["answer"])
        # Sample Output:
        # SAP runs certified environmental and energy management systems that include ISO 14001 and ISO 50001.

response = retrieval_chain.invoke({"input": "How much does SAP intend to reduce its carbon emissions for the rest of 2025?"})
print(response["answer"])
        # Sample Output:
        # The provided context does not specify a specific target for reducing carbon emissions for the rest of 2025. It mentions SAP's commitment to becoming carbon neutral in its own operations by 2023 and achieving net-zero along its value chain by 2030, but it does not detail any specific reduction goals for 2025.

response = retrieval_chain.invoke({"input": "what are the key environmental objectives to foster a low-carbon, circular future"})
print(response["answer"])
        # Sample Output:
        # The key environmental objectives to foster a low-carbon, circular future as outlined in the context are:
        # 
        # 1. Become carbon neutral in SAP's own operations by 2023.
        # 2. Achieve net-zero along SAP's value chain in line with a 1.5°C future by 2030.
        # 3. Continually improve SAP’s energy performance.
        # 4. Strive towards zero electronic waste in SAP's own operations by 2030.
        # 5. Improve SAP’s overall waste performance and separation.
        # 6. Continually reduce SAP’s water consumption.
        # 7. Raise awareness for sustainability and enable employees to improve SAP’s environmental performance.
        # 8. Develop solutions that enable customers to meet their sustainability challenges and opportunities.

response = retrieval_chain.invoke({"input": "What are the reimbursable expenses? Can I attend a conference that falls on a Sunday?"})
print(response["answer"])
        # Sample Output:
        # The reimbursable expenses according to the SAP Global Travel Policy include:
        # 
        # - Transportation
        # - Parking fees
        # - Cost of private car usage based on local reimbursement rates
        # - Accommodation
        # - Cancellation fees
        # - Meals in accordance with the country-specific rules defined in the local amendments
        # - Course and seminar fees
        # - Tips (local practice in the destination country)
        # - Laundry services while on the trip
        # - Communication costs incurred during day-to-day business
        # - Baggage fees
        # - Purchase of business-required low-value items (up to €100)
        # - Charges for currency exchanges
        # - Gifts for business partners (in alignment with SAP’s and business partner’s policies)
        # - Business-relevant entertainment costs (in alignment with SAP’s and business partner’s policies)
        # - Car services (please refer to the local amendment)
        # 
        # Regarding attending a conference that falls on a Sunday, the policy does not explicitly mention restrictions on attending events based on the day of the week. Therefore, you should be able to attend a conference on a Sunday, provided it is related to your business activities and complies with the overall travel policy. However, it is advisable to check with your manager or refer to any local amendments for specific guidelines.

response = retrieval_chain.invoke({"input": "Can I book a hotel that is not a SAP preferred hotel?"})
print(response["answer"])
        # Sample Output:
        # Yes, you can book a hotel that is not a SAP-preferred hotel if either of the following conditions is met:
        # 
        # 1. There is no SAP-preferred hotel within a reasonable distance from the travel destination.
        # 2. Another hotel is cheaper than the SAP-preferred hotel, taking into consideration the amenities included.
        # 
        # Additionally, the use of apartments or flats is specifically regulated in the local amendment.




