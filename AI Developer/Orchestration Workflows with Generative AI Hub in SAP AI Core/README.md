# Orchestration Workflows With SAP Cloud SDK for AI (Python)

## Lesson 1: Orchestration Basics
### Introduction
In SAP’s Generative AI Hub, “orchestration” is the process of combining modular steps—like prompt templating and model invocation—into a cohesive pipeline. By leveraging the Generative AI Hub SDK, you can configure templates, choose an LLM, and run everything with a single API call. This is crucial in business settings where consistent, controlled AI outputs are needed across multiple workflows.

### Key Concepts
- **Template**: A predefined structure for prompts, ensuring consistency and easier maintenance.
- **LLM Config**: A Large Language Model configuration, specifying which model (e.g., “gemini-1.5-flash”) to use and how (max tokens, temperature, etc.).
- **Orchestration Config**: Binds the template and model together, possibly including other modules (e.g., data masking or content filtering).
- **Orchestration Service**: The object responsible for running the pipeline and returning the model’s output.


#### Load the LLM Keys
```python
import os
import json
    
# Load your service key from a Secret Store
secret = dbutils.secrets.get(scope="PROD_XGTP_SCOPE", key="LEARNING_GENAIXL")
svcKey = json.loads(secret) 
# Set environment variables
os.environ["AICORE_AUTH_URL"] = svcKey["url"]
os.environ["AICORE_CLIENT_ID"] = svcKey["clientid"]
os.environ["AICORE_CLIENT_SECRET"] = svcKey["clientsecret"]
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = svcKey["serviceurls"]["AI_API_URL"]
```


```python
import pathlib

from gen_ai_hub.proxy import get_proxy_client
from ai_api_client_sdk.models.status import Status
from gen_ai_hub.orchestration.service import OrchestrationService
client = get_proxy_client()
orchestration_service = OrchestrationService()
```


```python
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
```
