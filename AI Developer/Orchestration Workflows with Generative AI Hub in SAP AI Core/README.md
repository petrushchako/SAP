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

```sh
    Extracted JSON: ```json
    {
      "sender": "bob@company.com",
      "subject": "Quarterly Report Discussion",
      "body": "Hello Team,\n\nLet's schedule a call to talk about the Q2 report next week.\nRegards,\nBob"
    }
    ```
```


> As you can see, the model includes additional formatting text (```json and ```) around the actual JSON output. While this is readable for humans, it's not ideal for applications that need to parse the JSON directly.


<br><br><br>


### Structured JSON Output with `response_format` Parameter

```python
from gen_ai_hub.orchestration.models.response_format import ResponseFormatJsonSchema


# 1. Define the exact JSON schema we want the AI to return.
email_schema = {
    "title": "Email",
    "type": "object",
    "properties": {
            "sender": {
            "type": "string",
            "description": "The email address of the sender."
        },
            "subject": {
            "type": "string",
            "description": "The subject line of the email."
        },
            "body": {
            "type": "string",
            "description": "The main content of the email."
        }
    },
    "required": ["sender", "subject", "body"]
}

# 2. Create a new template using the response_format parameter.
#    Note that we no longer need to explicitly ask for JSON in the system prompt.
template_with_schema = Template(
    messages=[
        SystemMessage("You are an AI assistant that extracts structured data from unstructured text."),
        UserMessage("{{?email_text}}")
    ],
    response_format = ResponseFormatJsonSchema(name="email_extractor", description="Extracts fields from an email", schema=email_schema),
)

# 3. Build a new OrchestrationConfig with the schema-enforced template.
config_with_schema = OrchestrationConfig(
    template=template_with_schema,
    llm=llm
)

# 4. Run the pipeline again with the new configuration.
result_with_schema = orchestration_service.run(config=config_with_schema,
    template_values=[TemplateValue(name="email_text", value=unstructured_email)]
)

# 5. Print the clean response and parse it to demonstrate it's valid JSON.
ai_response_clean = result_with_schema.orchestration_result.choices[0].message.content
print("Clean JSON Output:", ai_response_clean)

# Prove that the output is a directly parsable JSON string
parsed_json = json.loads(ai_response_clean)
print("\nParsed Dictionary Object:")
print(parsed_json)
print("\nSender:", parsed_json.get("sender"))
```

```sh
    Clean JSON Output: {
      "sender": "bob@company.com",
      "subject": "Quarterly Report Discussion",
      "body": "Hello Team, Let's schedule a call to talk about the Q2 report next week. Regards, Bob"
    }
    
    Parsed Dictionary Object:
    {'sender': 'bob@company.com', 'subject': 'Quarterly Report Discussion', 'body': "Hello Team, Let's schedule a call to talk about the Q2 report next week. Regards, Bob"}
    
    Sender: bob@company.com
```

#### Summary:
- **LLM**: Sets up the desired model (in this case, “gemini-2.5-flash”) and optional parameters like temperature. Other models you can use in the present deployment are: ['anthropic--claude-4-sonnet, gemini-2.5-pro, 'gpt-5', 'gpt-5-mini', ]
- **Template**: Outlines the prompt structure with placeholders (e.g., {{?topic}}).
- **OrchestrationConfig**: Ties everything together.
- **OrchestrationService**: Executes the pipeline, sending your prompt to the chosen LLM.
- **Run**: Substitutes the {{?topic}} placeholder and prints the model’s output.


<br><br><br>

## Lesson 2: Data Masking and Privacy
#### Introduction
In enterprise settings, large language models frequently process sensitive user or corporate data. Data Masking is a core capability to automatically anonymize or pseudonymize personal information—like names, phone numbers, or emails—before it’s sent to the model. By applying data masking, you protect users’ privacy while still benefiting from AI-driven insights.

### Key Concepts
- **Anonymization vs. Pseudonymization**:
    - **Anonymization**: Irreversibly replaces personal data with placeholders (e.g., “[PERSON]”).
    - **Pseudonymization**: Uses reversible tokens (e.g., “[PERSON_ID_123]”) that can later be mapped back if needed.
- **Profile Entities**: Predefined categories of sensitive data, such as EMAIL, PHONE, PERSON, ORG, and so on.
- **SAPDataPrivacyIntegration**: A component of the SAP Generative AI Hub SDK that handles detection and masking of sensitive data in prompts or outputs.


Below is a simplified example using the SAP Cloud SDK for AI to set up an orchestration pipeline with data masking. We’ll focus on anonymizing personal data in the user’s input:

```python
# Import the data masking tools
from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import (
    SAPDataPrivacyIntegration, MaskingMethod, ProfileEntity
)

# 1. Define the LLM
llm = LLM(
    name="mistralai--mistral-small-instruct",
    version="latest",
    parameters={"temperature": 0.2, "max_tokens": 150},
)

# 2. Create a prompt template that includes user text
template = Template(
    messages=[
        UserMessage("User input: {{?user_text}}")
    ]
)

# 3. Configure Data Masking (anonymize person and phone entities)
data_masking = DataMasking(
    providers=[
        SAPDataPrivacyIntegration(
            method=MaskingMethod.ANONYMIZATION,
            entities=[ProfileEntity.PERSON, ProfileEntity.PHONE]
        )
    ]
)

# 4. Build an OrchestrationConfig
config = OrchestrationConfig(
    template=template,
    llm=llm
)

# 5. Attach Data Masking to the config
config.data_masking = data_masking

# 6. Run a test
result = orchestration_service.run(config=config,
    template_values=[TemplateValue(
        name="user_text",
        value="Hello, my name is John Doe and my phone number is +1-202-555-0147."
    )]
)

# Print the final output
print("Masked AI Output:", result.orchestration_result.choices[0].message.content)
```

```sh
Masked AI Output: It seems like you're providing some personal information, but it's masked. If you need assistance with something specific, feel free to let me know how I can help! If you're looking to share information securely, please ensure you're using a secure method and that you trust the recipient.
```

> See the Orchestration service documentation to know more about other [masking types](https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/_reference/orchestration-service.html#masking-types)



### Summary
- `DataMasking` is set to anonymization, targeting `ProfileEntity.PERSON` and `ProfileEntity.PHONE`.
- The user’s input—`“John Doe”` and a phone number—is automatically detected and replaced with a placeholder.
- The LLM then receives already-masked content, safeguarding sensitive data.



