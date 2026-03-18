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



### Excercise
#### 1. Define the LLM configuration
```python
llm = LLM(
    name="gemini-2.5-flash",
    version="latest",
    parameters={"temperature": 0.2, "max_tokens": 256},
)
```

#### 2. Create a prompt template
- The system message instructs the AI to produce JSON output.
- The user message passes the unstructured text (an email in this case).

```python
template = Template(
    messages=[
        SystemMessage(
            "You are an AI assistant that extracts structured data from unstructured emails. "
            "Please read the email text and output a JSON object with the fields: "
            "'sender', 'subject', and 'body'."
        ),
        UserMessage("Email text: {{?email_text}}")
    ]
)
```
> In addtiion to the messages dictionary, the Template class also allows to define default values for template input parameter values. See an [example here](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/_reference/orchestration-service.html#step-1-define-the-template-and-default-input-values).

#### 3. Build an OrchestrationConfig with the template and the LLM
```python
config = OrchestrationConfig(
    template=template,
    llm=llm
)
```

#### 4. Run the pipeline with a sample email
```python
unstructured_email = (
    "From: bob@company.com\n"
    "Subject: Quarterly Report Discussion\n"
    "Hello Team,\n\n"
    "Let's schedule a call to talk about the Q2 report next week.\n"
    "Regards,\n"
    "Bob"
)
```

#### 5. Substitutes the {{?email_text}} placeholder and executes the pipeline, sending your prompt to the chosen LLM and its configuration
```python
result = orchestration_service.run(config=config,
    template_values=[TemplateValue(name="email_text", value=unstructured_email)]
)
```


#### 6. Print the AI’s JSON-like response
```python
ai_response = result.orchestration_result.choices[0].message.content
print("Extracted JSON:", ai_response)
```

> As you can see, the model includes additional formatting text (```json and ```) around the actual JSON output. While this is readable for humans, it's not ideal for applications that need to parse the JSON directly.


<br>
