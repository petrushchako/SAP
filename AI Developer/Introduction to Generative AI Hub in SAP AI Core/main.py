import os
import json
    
# Load your service key from a Secret Store
secret = dbutils.secrets.get(scope="PROD_XGTP_SCOPE", key="LEARNING_GENAIXL")
svcKey = json.loads(secret) 
# Set environment variables so that SAP Cloud SDK can use them for authentication
os.environ["AICORE_AUTH_URL"] = svcKey["url"]
os.environ["AICORE_CLIENT_ID"] = svcKey["clientid"]
os.environ["AICORE_CLIENT_SECRET"] = svcKey["clientsecret"]
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = svcKey["serviceurls"]["AI_API_URL"]


##################################################################################


from gen_ai_hub.proxy.langchain.init_models import init_llm
 
llm = init_llm('gpt-4o-mini', temperature=0.0, max_tokens=1024)

# Long reposnse
response = llm.invoke('How do LLMs work?').content 
# print('Response:', response)

# Simplified response
response-short = llm.invoke('Summarize the following text in one sentence to an impatient developer: ' + response).content 
print('Response:', response-short)

# LLM evolution history
response-history = llm.invoke('Produce an ASCII-based timeline or scale showing the origins and evolution of these large language models. Display each model according to its year, vendor, and number of parameters. Go until 2025 if possible').content 
print('Response:', response-history)

# Feasibility of Building an LLM: A Model's Perspective
response-train-llm = llm.invoke('Explain in a few sentences how feasible it is for most organizations, especially those new to the field, to develop a cutting-edge language model?').content 
print('Response:', response-train-llm)
