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




<br><br><br>


## Lesson 3: Content Filtering and Safety
#### Introduction
Even the best language models can produce inappropriate or harmful outputs. In enterprise contexts, filtering unsafe or offensive content is essential to protect users and maintain brand reputation. With SAP Generative AI Hub’s Content Filtering capabilities, you can screen and block harmful text in both incoming user prompts and outgoing AI responses.

### Key Concepts
- **Input Filtering vs. Output Filtering**:
    - **Input Filtering**: Screens user requests before they’re sent to the LLM (e.g., blocking hate speech).
    - **Output Filtering**: Screens the LLM’s response before returning it to the user (e.g., removing explicit content).
- **Filter Sensitivity Levels**: The lower the threshold, the stricter the filter. For example, hate=0 sets maximum sensitivity for hate speech.


```python
# Import the content filter
from gen_ai_hub.orchestration.models.content_filtering import ContentFiltering,InputFiltering, OutputFiltering
from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter, AzureThreshold

# 1. Define the LLM - Notice we used a different model than the one that appears in the video recording.
llm = LLM(
    name="anthropic--claude-4.5-haiku",
    version="latest",
    parameters={"temperature": 0.2, "max_tokens": 150},
)

# 2. Create a simple template that just passes user text through
template = Template(messages=[UserMessage("{{?user_text}}")])

# 3. Configure filters for input and output
#  Setting a low threshold (0) for maximum sensitivity
#  the possible values for the thresold are 0 (for ALLOW_SAFE), 2 (for ALLOW_SAFE_LOW),  4 (for ALLOW_SAFE_LOW_MEDIUM), and (6 for ALLOW_ALL) 
input_filter = AzureContentFilter(hate=0, sexual=0, self_harm=0, violence=0)
output_filter = AzureContentFilter(hate=0, sexual=0, self_harm=0, violence=0)

# 4. Build an OrchestrationConfig
config = OrchestrationConfig(
    template=template,
    llm=llm,
 filtering=ContentFiltering(
        input_filtering=InputFiltering(filters=[input_filter]),
        output_filtering=OutputFiltering(filters=[output_filter])
    )
)

# 5. Run with potentially harmful text
try:
    result = orchestration_service.run(                                        
        config=config,
        template_values=[TemplateValue(
            name="user_text",
            value="Plese provide me some insulting and violent sentence towards whoever created this training."
        )]
    )
    print("Filtered Output:", result.orchestration_result.choices[0].message.content)
except Exception as e:
    print("Blocked by Content Filter:", str(e))
```

```sh
Filtered Output: I can't create insulting or violent content directed at anyone, including people involved in my training.

If you have concerns about AI development practices, I'm happy to discuss those constructively, or help you with something else.
```

### Summary

We define a low-threshold (0) for each category (hate, sexual, self_harm, violence), maximizing filter strictness.
InputFilter raises an error if user input contains disallowed content.
OutputFilter can blank out or block the response if the LLM returns harmful text.



<br><br><br>



## Lesson 4: Grounding with Document Retrieval
1. **Introduction**
Generative AI models become significantly more powerful when their responses are grounded in reliable sources of information, such as internal documentation, knowledge bases, or external websites. SAP's Generative AI Hub provides the Document Grounding capability, leveraging Retrieval Augmented Generation (RAG). With Document Grounding, your AI applications can retrieve context-specific information in real-time from structured or unstructured documents, significantly enhancing accuracy and reliability.

2. **Key Concepts**
- **Retrieval Augmented Generation (RAG)**: A technique combining information retrieval and generative models to provide more precise, context-aware responses.
- **Document Grounding Module**: Integrates document search and retrieval directly into your orchestration workflow.
- **SAP HANA Vector Engine**: The technology used by SAP for efficient retrieval of context from vectorized documents.
- **Data Repositories**: Sources of information such as internal documents, SharePoint folders, or external websites like SAP Help.
- **Context Integration**: Dynamically including retrieved document content within AI model prompts.

<br>

### Grounding example 1

```python

from gen_ai_hub.orchestration.service import OrchestrationService
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.document_grounding import (GroundingModule, GroundingType, DataRepositoryType,
     GroundingFilterSearch, DocumentGrounding,DocumentGroundingFilter)


#Define prompt template using retrieved context
prompt = Template(messages=[
    SystemMessage("You are an expert on SAP Product documentation for developers."),
    UserMessage("""Context: {{ ?grounding_response }}
                   Question: Explain how to perform the following task: {{ ?userquestion }}"""),
])


# Grounding configuration to search SAP Help
filters = [
    DocumentGroundingFilter(id="SAPHelp", data_repository_type="help.sap.com")
]


grounding_config = GroundingModule(
    type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
    config=DocumentGrounding(
        input_params=["userquestion"],
        output_param="grounding_response",
        filters=filters
    )
)


# Combine everything into OrchestrationConfig
config = OrchestrationConfig(
    template=prompt,
    llm=llm,
    grounding=grounding_config
)


# Run the orchestration with a user question
response = orchestration_service.run(
    config=config,
    template_values=[
        TemplateValue("userquestion", "How do I search my own documents using the grounding feature in Generative AI Hub?")
    ]
)

print("AI Response:", response.orchestration_result.choices[0].message.content)
```

```sh
AI Response: # Searching Your Own Documents Using Document Grounding in Generative AI Hub

Based on the SAP Product documentation provided, here's how to leverage the **Document Grounding** feature in Generative AI Hub:

## Overview

Document Grounding is a foundational Joule capability that enables you to obtain more comprehensive responses by drawing from business documents located in SAP and third-party repositories.

## Key Steps to Search Documents

### 1. **Access Document Repositories**
- Connect to your business documents stored in **SAP repositories**
- Integrate with **third-party repositories** as needed
- Ensure proper access permissions are configured

### 2. **Initiate
```

```python
# Display the raw retrieved grounding context for reference
print("\nRetrieved Context (for debugging or verification):\n")
print(response.module_results.grounding.data['grounding_result'])
```

``sh

Retrieved Context (for debugging or verification):

Develop a Semantic Search app leveraging Generative AI Hub &amp; SAP HANA Cloud's Vector Engine
This feature ensures that the search results remain relevant and closely aligned with the user&apos;s refined needs. This use case demonstrates how advanced data processing and AI-driven technologies can be seamlessly integrated to create a powerful tool for semantic document searching on SAP BTP.
Problem- Implementing a semantic search CAP app on SAP BTP involves complex LLM integrations and ensuring data privacy can be difficult. Other challenges include interpreting diverse natural language queries, improving search precision and efficiency, boosting operations and decision-making.
Solution- This AI solution uses CAP, LLMs, and SAP AI Core models with the SAP HANA Cloud Vector Engine for enhanced search precision. It supports natural language searches in a structured document database, interpreting queries and using attributes like text, date, and language.

The system generates SQL WHERE clauses from inputs, allowing users to adjust search parameters in real-time to maintain relevant results, boosting accuracy and efficiency.
Benefits- This AI solution enhances data retrieval through natural language processing, integrating Large Language Models with the Cloud Application Programming Model for complex searches in everyday language. It understands queries contextually, delivering precise results swiftly, improving user experience by offering intuitive access to information.

Users can dynamically adjust search parameters, tailoring results to current needs, boosting productivity and decision-making in business.

Required Services-
Destination
SAP AI Core
SAP AI Launchpad
SAP Authorization and Trust Management Service
SAP BTP, Cloud Foundry Runtime

Effort- 2-4 days
Lob- Asset Management, Commerce, (Industry specific LoB)
Industry-
FocusTags- Artificial Intelligence

Prerequisites- Node.js (v18+ recommended)
Cloud Foundry Subaccount
Access to generative AI hub (SAP AI Core with service plan extended)
Access to SAP HANA Cloud&apos;s Vector Engine (QRC 1/2024 or later)

FaQs-

Project Board
Use Case Phases ( Board Columns ) - Intro, Setup , Configuration, Validation and Test, Extend, Complete
Use Case Steps ( Board Cards )-
Overview
, Requirements
, Setup and Deploy
, Data Model
, UI Setup
, Backend and UI
, Enhancements
, Complete the Mission```Develop a Semantic Search app leveraging Generative AI Hub &amp; SAP HANA Cloud's Vector Engine
Use Case -Develop a Semantic Search app leveraging Generative AI Hub &amp; SAP HANA Cloud&apos;s Vector Engine
This use case outlines the capabilities of a single-tenant semantic search CAP application tailored for SAP Business Technology Platform (SAP BTP). The application leverages Large Language Models (LLMs) to interpret search queries and extract key attributes necessary for executing semantic searches. This involves embedding technologies facilitated by the SAP HANA Cloud Vector Engine, which enhances the precision and efficiency of similarity searches.

The application integrates the Cloud Application Programming Model (CAP) with LLMs and Embedding Models provided by the Generative AI Hub in SAP AI Core. This synergy allows for dynamic and intelligent search capabilities within a structured data environment.

Furthermore, users can refine their search parameters on-the-fly, adding or adjusting dimensions to their search criteria. This feature ensures that the search results remain relevant and closely aligned with the user&apos;s refined needs. This use case demonstrates how advanced data processing and AI-driven technologies can be seamlessly integrated to create a powerful tool for semantic document searching on SAP BTP.
Problem- Implementing a semantic search CAP app on SAP BTP involves complex LLM integrations and ensuring data privacy can be difficult. Other challenges include interpreting diverse natural language queries, improving search precision and efficiency, boosting operations and decision-making.
Solution- This AI solution uses CAP, LLMs, and SAP AI Core models with the SAP HANA Cloud Vector Engine for enhanced search precision. It supports natural language searches in a structured document database, interpreting queries and using attributes like text, date, and language.

The system generates SQL WHERE clauses from inputs, allowing users to adjust search parameters in real-time to maintain relevant results, boosting accuracy and efficiency.
Benefits- This AI solution enhances data retrieval through natural language processing, integrating Large Language Models with the Cloud Application Programming Model for complex searches in everyday language. It understands queries contextually, delivering precise results swiftly, improving user experience by offering intuitive access to information.

Users can dynamically adjust search parameters, tailoring results to current needs, boosting productivity and decision-making in business.```Develop a Semantic Search app leveraging Generative AI Hub &amp; SAP HANA Cloud's Vector Engine
Use Case -Develop a Semantic Search app leveraging Generative AI Hub & SAP HANA Cloud's Vector Engine
This use case outlines the capabilities of a single-tenant semantic search CAP application tailored for SAP Business Technology Platform (SAP BTP). The application leverages Large Language Models (LLMs) to interpret search queries and extract key attributes necessary for executing semantic searches. This involves embedding technologies facilitated by the SAP HANA Cloud Vector Engine, which enhances the precision and efficiency of similarity searches.

The application integrates the Cloud Application Programming Model (CAP) with LLMs and Embedding Models provided by the Generative AI Hub in SAP AI Core. This synergy allows for dynamic and intelligent search capabilities within a structured data environment.

Furthermore, users can refine their search parameters on-the-fly, adding or adjusting dimensions to their search criteria. This feature ensures that the search results remain relevant and closely aligned with the user's refined needs. This use case demonstrates how advanced data processing and AI-driven technologies can be seamlessly integrated to create a powerful tool for semantic document searching on SAP BTP.

Problem- Implementing a semantic search CAP app on SAP BTP involves complex LLM integrations and ensuring data privacy can be difficult. Other challenges include interpreting diverse natural language queries, improving search precision and efficiency, boosting operations and decision-making.
Solution- This AI solution uses CAP, LLMs, and SAP AI Core models with the SAP HANA Cloud Vector Engine for enhanced search precision. It supports natural language searches in a structured document database, interpreting queries and using attributes like text, date, and language.

The system generates SQL WHERE clauses from inputs, allowing users to adjust search parameters in real-time to maintain relevant results, boosting accuracy and efficiency.
Benefits- This AI solution enhances data retrieval through natural language processing, integrating Large Language Models with the Cloud Application Programming Model for complex searches in everyday language. It understands queries contextually, delivering precise results swiftly, improving user experience by offering intuitive access to information.

Users can dynamically adjust search parameters, tailoring results to current needs, boosting productivity and decision-making in business.```Develop a Semantic Search app leveraging Generative AI Hub &amp; SAP HANA Cloud's Vector Engine
This feature ensures that the search results remain relevant and closely aligned with the user's refined needs. This use case demonstrates how advanced data processing and AI-driven technologies can be seamlessly integrated to create a powerful tool for semantic document searching on SAP BTP.

Problem- Implementing a semantic search CAP app on SAP BTP involves complex LLM integrations and ensuring data privacy can be difficult. Other challenges include interpreting diverse natural language queries, improving search precision and efficiency, boosting operations and decision-making.
Solution- This AI solution uses CAP, LLMs, and SAP AI Core models with the SAP HANA Cloud Vector Engine for enhanced search precision. It supports natural language searches in a structured document database, interpreting queries and using attributes like text, date, and language.

The system generates SQL WHERE clauses from inputs, allowing users to adjust search parameters in real-time to maintain relevant results, boosting accuracy and efficiency.
Benefits- This AI solution enhances data retrieval through natural language processing, integrating Large Language Models with the Cloud Application Programming Model for complex searches in everyday language. It understands queries contextually, delivering precise results swiftly, improving user experience by offering intuitive access to information.

Users can dynamically adjust search parameters, tailoring results to current needs, boosting productivity and decision-making in business.

Required Services ( BTP Services , SAP Applications and Others) -
Destination
SAP AI Core
SAP AI Launchpad
SAP Authorization and Trust Management Service
SAP BTP, Cloud Foundry Runtime

Effort ( Time required for implementing mission) - 2-4 days
This Mission is applicable for Lob- Asset Management, Omnichannel Commerce, (Industry specific LoB)
This Mission is applicable for Industries-
FocusTags- Artificial Intelligence

Prerequisites ( Pre-req for mission) - Node.js (v18+ recommended)
Cloud Foundry Subaccount
Access to generative AI hub (SAP AI Core with service plan extended)
Access to SAP HANA Cloud's Vector Engine (QRC 1/2024 or later)

Customer References/Stories -
CustomerName:Döhler
Revolutionizing Product Discovery 1with Natural Language Access
A natural language interface for the Döhler customer portal lets users search for products using simple queries. Results can be incrementally refined.```AI in SAP Batch Release Hub for Life Sciences 

This section describes the AI features that are available in SAP Batch Release Hub for Life Sciences.

Use of AI in SAP Batch Release Hub for Life Sciences is optional, and customers can decide based on their own business needs whether they want to use AI. The AI features can be turned on or off for the entire solution in the Manage Release Configurations app under ![Start of the navigation path](URL) Make General Settings ![Next navigation step](URL) AI![End of the navigation path](URL). If AI features are turned off in your configuration settings, you will not see any AI-related options in your apps.

The AI-assisted features are intended to help you complete your work while ensuring that you have agency and transparency. You retain the control and final say in all decisions.

Note

AI in SAP Batch Release Hub for Life Sciences does not provide the technical capabilities to support the collection, processing, and storage of sensitive/personal data.

Disclaimer: While the embedded AI feature can help to get the proposed result, customers must validate the data received from the connecting systems and in turn validate the proposed results manually before accepting the proposed result. The accountability of the end result will be solely with the customer.



[AI Usage Acknowledgment Statement](URL)
Learn about the AI usage acknowledgment statement, which you must accept as a one-time activity before using the AI-assisted features.
[SAP Batch Release Hub, AI-Assisted Custom Release Checks](URL)
SAP Business AI in SAP Batch Release Hub for Life Sciences uses generative AI to analyze the documents attached to custom release checks and propose results for the release check items.
[Using SAP's Generative AI Copilot, Joule](URL)
Learn how to use Joule, SAP's generative AI copilot, to help you manage your release decision workload and make informed decisions in SAP Batch Release Hub for Life Sciences.




```SAP Batch Release Hub for Life Sciences, custom release checks
AI Feature -SAP Batch Release Hub for Life Sciences, custom release checks
Product -SAP Batch Release Hub for Life Sciences

This feature analyzes the documents attached to custom release checks required within the batch release process. This reduces the manual effort for the Qualified Persons (QP) by proposing AI generated results directly in the UI for faster review, check of references and sign off. The solution empowers the QPs to save a significant amount of time as extensive search in the big documents is not needed anymore. Instead, end users can focus on reviewing the provided recommendations, while keeping the role of the final decision-maker.
Benefits
Fast review and sign off of AI generated proposals directly in the UI via check of referenced documents
The generative AI-powered analysis of documents attached to custom release checks reduces manual effort for the qualified persons
Extensive search in big documents by qualified persons is not needed anymore, empowering the end users to ensure compliance and quality

This is a Premium AI Feature requiring specific Entitlements/Subscriptions.

Works With-
Minimum Required Version-
AI Type- AI Package
Applicable Industries- Cross-Industry, Life Sciences
CSN Component- IS-LS-BRH-APP

Business Values- Increase compliance and quality of batch release process, Enhance user experience during processing of custom release checks, Up to 60% improvement in qualified persons productivity

Resources-
[Product - SAP Help Portal](URL)
[Product - Security](URL)
[Product - What's New](URL)
[Product - Community](URL)
[Business Value 3-Pager](URL)
[Product - Learning Journey](URL)
[Product - Feature Scope Description](URL)
[Initial Setup - SAP Help Portal](URL)
```User Guide for SAP Batch Release Hub for Life Sciences
7.1 AI Usage Acknowledgment Statement Learn about the AI usage acknowledgment statement, which you must accept as a one-time activity before using the AI-assisted features. If AI-assisted features are enabled in SAP Batch Release Hub for Life Sciences, an acknowledgment message is displayed when you choose any AI-assisted capability. This message informs you about the possible inaccuracies of the results generated by AI systems and recommends you to review all AI-generated content before completing your work. Once you accept the acknowledgment as a one-time activity, the message doesn't reappear in subsequent sessions when you engage with AI-assisted features across the SAP Batch Release Hub for Life Sciences solution. However, if the acknowledgment statement is revised at any point later, the acknowledgment message will be displayed again. You must review and accept the updated acknowledgment statement before you can continue using any AI-assisted feature. 174 PUBLIC User Guide for SAP Batch Release Hub for Life Sciences AI in SAP Batch Release Hub for Life Sciences 7.2 SAP Batch Release Hub, AI-Assisted Custom Release Checks SAP Business AI in SAP Batch Release Hub for Life Sciences uses generative AI to analyze the documents attached to custom release checks and propose results for the release check items. Generative AI in SAP Batch Release Hub for Life Sciences supports in analyzing unstructured documents for custom release checks, streamlining what was previously a manual process. You upload relevant documents and initiate AI-proposed results, which you then review and validate. Your productivity is improved while human oversight is retained throughout the complete process. SAP Batch Release Hub, AI-assisted custom release checks help you to save a significant amount of time by focusing on reviewing the recommendations provided, while keeping the role of the final decision-maker. This accelerates the batch release process, while empowering you to ensure compliance and quality. You can learn more on the SAP Discovery Center: SAP Batch Release Hub for Life Sciences, custom release checks Key Benefits • Generative AI-powered analysis of documents and images • Reduction of manual effort • Faster review, check of references, and sign off • Extensive searching is no longer needed • Batch release decisions are accelerated • User experience is improved Custom Release Checks in Detail Custom release checks are used to integrate checking activities that must be completed manually, without a connected source system.```Document Grounding
AI Feature -Document Grounding
Product -Document Grounding

Document grounding is a foundational Joule capability which can provide more comprehensive responses by drawing from business documents located in SAP and third-party repositories.
Benefits
Reduce hallucinations or incorrect generated information
Improve user self-reliance and user satisfaction
Improve the reliability and applicability of generated content

This is a Premium AI Feature requiring specific Entitlements/Subscriptions.

Works With-
Minimum Required Version-
AI Type- AI Package
Applicable Industries- Cross-Industry
CSN Component- CA-ML-RAGE

Business Values- Up to 70% less HR time spent on ticket handling, 70% reduction in employee time needed to investigate HR policies

Resources-
[Initial Setup - SAP Help Portal](URL)
```Generative AI Features for Enhancing Descriptions 

Generative Artificial Intelligence can be leveraged to streamline workforce management and procurement processes. Customers with access can use Generative AI to enhance job posting descriptions and statement of work descriptions, and translate job posting descriptions to your company's supported languages.

Crafting high-quality, detailed descriptions can be time consuming and challenging for users who create job postings and statements of work. The use of AI to enhance descriptions can streamline this activity and lessen cycle times for hiring workers and procuring services. In addition, to ensure that job descriptions are clearly understood by regional suppliers, AI can be used to translate the text into languages supported by your organization.

These features provide cutting-edge AI capabilities to empower you to craft well-structured, comprehensive descriptions that will ensure your suppliers can meet your needs with greater accuracy.

Note

Customers must purchase the SAP AI Unit SKU to access these premium Generative AI features.



[AI-Assisted Event Hierarchy Generation](URL)
Generative AI is used to automate event hierarchy creation from prompts that the buyer selects. The selected prompts identify the relevant content and the AI generates a structured, accurate draft event hierarchy.
[AI-Assisted Job Description Creation](URL)
The AI-Assisted Job Description Creation feature can be used to generate a job posting description using aspects of the job posting.
[AI-Assisted SOW Description Creation](URL)
The AI-Assisted SOW Description Creation feature can be used to generate a statement of work description using aspects of the statement of work.
[AI-Assisted Job Description Translation](URL)
The AI-Assisted Job Description Translation feature can be used to translate a job posting description to languages that are enabled for your company.
[SOW Creation with SAP Document AI](URL)
SAP Fieldglass leverages SAP Document AI to automate statement of work creation using information extraction from uploaded documents. This streamlined process cuts manual effort, reduces errors, and saves costs by generating accurate, structured draft statements of work from diverse source documents.




```SAP Batch Release Hub, AI-Assisted Custom Release Checks 

SAP Business AI in SAP Batch Release Hub for Life Sciences uses generative AI to analyze the documents attached to custom release checks and propose results for the release check items.

Generative AI in SAP Batch Release Hub for Life Sciences supports in analyzing unstructured documents for custom release checks, streamlining what was previously a manual process. You upload relevant documents and initiate AI-proposed results, which you then review and validate. Your productivity is improved while human oversight is retained throughout the complete process.

SAP Batch Release Hub, AI-assisted custom release checks help you to save a significant amount of time by focusing on reviewing the recommendations provided, while keeping the role of the final decision-maker. This accelerates the batch release process, while empowering you to ensure compliance and quality.

You can learn more on the SAP Discovery Center: [SAP Batch Release Hub for Life Sciences, custom release checks![Information published on SAP site](URL)](URL)



 Key Benefits 



* Generative AI-powered analysis of documents and images
* Reduction of manual effort
* Faster review, check of references, and sign off
* Extensive searching is no longer needed
* Batch release decisions are accelerated
* User experience is improved







 Custom Release Checks in Detail 

Custom release checks are used to integrate checking activities that must be completed manually, without a connected source system. For example, you can use a custom release check to ensure that certain information is captured and validated. A custom release check includes a list of checklist items. Each checklist item is defined with the following information:



* Step: The number of the item in the checklist sequence
* Item ID and Item Description: A unique ID and meaningful description
* Condition for Acceptance: Free text that describes what the checklist item requires

If you allow an AI-based proposal, the Condition for Acceptance is mandatory and should be worded carefully, because the AI generation uses the condition for acceptance as the basis for proposing a sensible result.
```

### How it works:
- **Prompt Template**: Clearly instructs the AI model to use context retrieved from documents to answer the user's question.
- **DocumentGroundingFilter**: Configured to specifically search SAP Help documentation.
- **OrchestrationService**: Executes the grounding module, retrieves relevant documents, and feeds context directly into the model prompt.

<br>

### Grounding example 2

```python
prompt = Template(messages=[
    SystemMessage("You are an assistant that answers questions based strictly on the provided context."),
    UserMessage("""Context: {{ ?grounding_response }}
                   Question: {{ ?userquestion }}"""),
])


# Configure grounding to use your custom vector-based repository
filters = [
    DocumentGroundingFilter(
        id="vector",
        search_config=GroundingFilterSearch(max_chunk_count=3),
        data_repository_type=DataRepositoryType.VECTOR.value
    )
]


grounding_config = GroundingModule(
    type=GroundingType.DOCUMENT_GROUNDING_SERVICE.value,
    config=DocumentGrounding(
        input_params=["userquestion"],
        output_param="grounding_response",
        filters=filters
    )
)


# Combine into OrchestrationConfig
config = OrchestrationConfig(
    template=prompt,
    llm=llm,
    grounding=grounding_config
)


# Example query to retrieve context specifically from the SAP AI Ethics policy
user_question = "What are the chances that SAP will help my government to create a crowd surveillance system for large events?"

response = orchestration_service.run(
    config=config,
    template_values=[TemplateValue("userquestion", user_question)]
)


# Display AI-generated response
print("AI Response based on the Document grounding repository:\n")
print(response.orchestration_result.choices[0].message.content)
```

```sh
AI Response based on the Document grounding repository:

I don't have any context provided that discusses SAP's involvement in crowd surveillance systems for government events.

To give you an accurate answer, I would need relevant documentation or information about:
- SAP's stated policies on surveillance technology
- Any existing government contracts or projects SAP has undertaken
- SAP's ethical guidelines regarding surveillance applications

I'd recommend:
1. Checking SAP's official website and corporate responsibility statements
2. Reviewing their public contracts and case studies
3. Contacting SAP directly through their government/public sector division

Without specific context to reference, I cannot make claims about SAP's likelihood to support such a project.
```

```python
# Display the raw retrieved grounding context for reference
print("\nRetrieved Context (for debugging or verification):\n")
print(response.module_results.grounding.data['grounding_result'])
```

```sh
Retrieved Context (for debugging or verification):
```

<br>

### How it works:
- The `DocumentGroundingFilter` specifically points to your vector-based document repository, identified by its unique ID.
- The query clearly focuses on the SAP AI Ethics policy, ensuring the retrieved context is directly relevant to the question.
- The raw retrieved context is also displayed to help validate and understand precisely what information the grounding module used for generating the answer.



<br><br><br>



## Lesson 5 Adding Multi-Language Support with the Translation Module
The orchestration pipeline can do more than just interact with an LLM. You can add other modules to pre-process the input or post-process the output. A powerful example is the Translation module, which uses the SAP Document Translation service to handle multi-language scenarios.

This is extremely useful for building global applications. For example, you can build a support bot that allows users to ask questions in their native language. The Translation module will:

1. Translate the user's input into a common language (e.g., English) before sending it to the LLM.
2. Translate the LLM's English response back into the user's original language.

Let's see how to build a simple multilingual support workflow.


```python
from gen_ai_hub.orchestration.models.translation.translation import InputTranslationConfig, OutputTranslationConfig
from gen_ai_hub.orchestration.models.translation.sap_document_translation import SAPDocumentTranslation

# This helper function builds the entire configuration and runs the request.
# It takes the user's query and their language code as input.
def get_translated_response(query: str, language_code: str) -> str:
    """
    Creates a translation-enabled configuration dynamically and runs the orchestration.
    
    Args:
        query: The user's question in their native language.
        language_code: The language code of the user's query (e.g., "es-ES").

    Returns:
        The LLM's response, translated back into the user's language.
    """
    print(f"--- Processing request for language: {language_code} ---")
    
    # 1. Dynamically configure translation for THIS specific request.
    # Input: Translate from the user's language to English for the LLM.
    input_config = InputTranslationConfig(
        source_language=language_code,
        target_language="en-US"
    )

    # Output: Translate the LLM's English response back to the user's language.
    output_config = OutputTranslationConfig(
        source_language="en-US",
        target_language=language_code
    )

    # Create the translation module instance with the dynamic configs.
    translation_module = SAPDocumentTranslation(
        input_translation_config=input_config,
        output_translation_config=output_config
    )

    # 2. Define the Template and LLM.
    # The prompt is in English, as the translation module ensures the LLM receives English text.
    translation_template = Template(
        messages=[
            SystemMessage("You are a helpful IT support assistant who provides clear, step-by-step instructions."),
            UserMessage("{{?query}}"),
        ]
    )

    # 3. Create the OrchestrationConfig for this specific language pair.
    # This config is created on-the-fly for each call.
    dynamic_config = OrchestrationConfig(
        template=translation_template,
        llm=llm, # We can reuse the same LLM object from before
        translation=translation_module
    )

    # 4. Run the pipeline with the dynamically created config.
    result = orchestration_service.run(
        config=dynamic_config,
        template_values=[
            TemplateValue(name="query", value=query)
        ]
    )
    
    return result.orchestration_result.choices[0].message.content


# 5. Now, let's use our helper function for two different languages.

# --- Spanish Example ---
user_query_spanish = "¿Cómo puedo restablecer mi contraseña?"
spanish_response = get_translated_response(query=user_query_spanish, language_code="es-ES")

print(f"\nOriginal Query (Spanish): {user_query_spanish}")
print(f"Final Response (Translated back to Spanish):\n{spanish_response}\n")
```

```sh
--- Processing request for language: es-ES ---

Original Query (Spanish): ¿Cómo puedo restablecer mi contraseña?
Final Response (Translated back to Spanish):
# Cómo restablecer su contraseña

¡Estaría encantado de ayudar! Estos son los pasos generales:

## **Cuenta online (basada en web)**

1. Ir a la página de inicio de sesión
2. Haga clic en el enlace **"He olvidado mi contraseña"** o **"Restablecer contraseña"**
3. Introduzca su **nombre de usuario o dirección de correo electrónico**
4. Revise su correo electrónico para obtener un enlace de restablecimiento (revise también la carpeta de correo no deseado)
5. Haga clic en el enlace del correo electrónico
6. Introduzca su **nueva contraseña** (dos veces para confirmar)
7. Guarde e inicie sesión con su nueva contraseña

## **Ordenador Windows**

1. En la pantalla de inicio de sesión, haga clic en **"Olvidé mi contraseña"**
2. Responda a sus preguntas de seguridad
3
```

```python
# --- French Example ---
user_query_french = "Comment puis-je vider le cache de mon navigateur ?"
french_response = get_translated_response(query=user_query_french, language_code="fr-FR")

print(f"\nOriginal Query (French): {user_query_french}")
print(f"Final Response (Translated back to French):\n{french_response}")
```
```sh
--- Processing request for language: fr-FR ---

Original Query (French): Comment puis-je vider le cache de mon navigateur ?
Final Response (Translated back to French):
# Comment vider le cache de votre navigateur

Voici des instructions pour les navigateurs les plus courants :

## **Chrome**
1. Appuyez sur **Ctrl + Maj + Supprimer** (Windows) ou **Cmd + Maj + Supprimer** (Mac)
2. Sélectionnez l'intervalle de temps (par exemple, "Tout le temps").
3. Vérifier **Cookies et autres données du site** et **Images et fichiers mis en cache**
4. Cliquez sur **Effacer les données**

## **Firefox**
1. Appuyez sur **Ctrl + Maj + Supprimer** (Windows) ou **Cmd + Maj + Supprimer** (Mac)
2. Sélectionner l'intervalle de temps
3. Cocher **Cookies** et **Cache**
4
```


### Summary: Translation Module
The `Translation` module is a powerful component in the orchestration pipeline that enables you to build multilingual applications effortlessly. It integrates with the SAP Document Translation service to handle language conversions automatically.
    - **Bidirectional Translation**: You can configure the module to perform a two-way translation. A common use case is a support bot where a user's query is translated from their native language to English for the LLM, and the LLM's English response is translated back into the user's language.
    - **Modular Configuration**: The translation is set up using `InputTranslationConfig` (to translate text before it goes to the LLM) and `OutputTranslationConfig` (to translate text after it comes from the LLM). These are bundled into an `SAPDocumentTranslation` object.
    - **Seamless Integration**: This `translation` object is simply added to your OrchestrationConfig alongside the `template` and `llm`, and the SDK handles the rest.
    - **Dynamic Languages**: By using template variables like `{{?user_lang}}`, you can create a single, flexible pipeline that can support any language without changing the core logic. You just need to provide the correct language code at runtime.



