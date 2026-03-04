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


from gen_ai_hub.proxy.langchain.init_models import init_llm
from gen_ai_hub.proxy.native.openai import chat

messages = [
    {"role": "system", "content": "You are a SAP customer support assistant"},
    {"role": "user", "content": "What is SAP AI chatbot useful for?"}
]

kwargs = dict(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100,    # Keep responses concise
        temperature=0.7,   # Adds some randomness
        top_p=0.1          # Highly focused on top-probability tokens
    )
response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']
print("Response:", message_value)
