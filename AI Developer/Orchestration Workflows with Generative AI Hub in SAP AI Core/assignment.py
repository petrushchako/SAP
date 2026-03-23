import json
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.response_format import ResponseFormatJsonSchema
from gen_ai_hub.orchestration.models.translation.translation import InputTranslationConfig
from gen_ai_hub.orchestration.models.translation.sap_document_translation import SAPDocumentTranslation
from gen_ai_hub.orchestration.models.content_filtering import ContentFiltering, InputFiltering
from gen_ai_hub.orchestration.models.azure_content_filter import AzureContentFilter
from gen_ai_hub.orchestration.models.data_masking import DataMasking
from gen_ai_hub.orchestration.models.sap_data_privacy_integration import (
    SAPDataPrivacyIntegration, MaskingMethod, ProfileEntity
)


import os
    
# Load your service key from a Secret Store
secret = dbutils.secrets.get(scope="PROD_XGTP_SCOPE", key="LEARNING_GENAIXL")
svcKey = json.loads(secret) 
# Set environment variables
os.environ["AICORE_AUTH_URL"] = svcKey["url"]
os.environ["AICORE_CLIENT_ID"] = svcKey["clientid"]
os.environ["AICORE_CLIENT_SECRET"] = svcKey["clientsecret"]
os.environ["AICORE_RESOURCE_GROUP"] = "default"
os.environ["AICORE_BASE_URL"] = svcKey["serviceurls"]["AI_API_URL"]

import pathlib

from gen_ai_hub.proxy import get_proxy_client
from ai_api_client_sdk.models.status import Status
from gen_ai_hub.orchestration.service import OrchestrationService

client = get_proxy_client()
orchestration_service = OrchestrationService()

from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.config import OrchestrationConfig



# Define the JSON Schema for extraction
social_media_schema = {
    "title": "SocialMediaPost",
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "content": {"type": "string", "description": "The English translation of the post body."},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "original_language": {"type": "string"}
    },
    "required": ["username", "content", "hashtags", "original_language"]
}

llm = LLM(
    name="gemini-2.5-flash",
    version="latest",
    parameters={"temperature": 0.2, "max_tokens": 1024},
)



def run_social_media_pipeline(post_text, lang_code):
    # 1. Translation Config (Input only)
    input_translation = InputTranslationConfig(source_language=lang_code, target_language="en-US")
    translation_module = SAPDocumentTranslation(input_translation_config=input_translation)

    # 2. Content Filtering (Strict hate speech filter)
    input_filter = AzureContentFilter(hate=0, sexual=0, self_harm=0, violence=0, PromptShield=True)
    content_filters = ContentFiltering(input_filtering=InputFiltering(filters=[input_filter]))

    # 3. Data Masking (PII protection)
    data_masking = DataMasking(
        providers=[SAPDataPrivacyIntegration(
            method=MaskingMethod.ANONYMIZATION,
            entities=[ProfileEntity.EMAIL, ProfileEntity.PHONE]
        )]
    )

    # 4. Template with JSON Schema
    template = Template(
        messages=[
            SystemMessage("Extract structured data from the social media post."),
            UserMessage("{{?post_text}}")
        ],
        response_format=ResponseFormatJsonSchema(
            name="post_extractor", 
            schema=social_media_schema
        )
    )

    # 5. Assemble Config
    config = OrchestrationConfig(
        template=template,
        llm=llm,
        translation=translation_module,
        filtering=content_filters,
        data_masking=data_masking
    )

    # 6. Run Orchestration
    try:
        result = orchestration_service.run(
            config=config,
            template_values=[TemplateValue(name="post_text", value=post_text)]
        )
        return result.orchestration_result.choices[0].message.content
    except Exception as e:
        return f"PIPELINE_ERROR: {str(e)}"
    



# Real post example: Olaf Scholz (German Chancellor)
german_post = "Gute Gespräche heute in Paris. Wir arbeiten gemeinsam für ein starkes Europa. #Souveränität #Europa"
print("Test 1 Result:", run_social_media_pipeline(german_post, "de-DE"))


# Spanish hateful phrase
hate_post = "Te odio, eres lo peor y mereces lo más violento."
print("Test 2 Result:", run_social_media_pipeline(hate_post, "es-ES"))


# French post with PII
pii_post = "Contactez mon bureau à contact@elysee.fr ou au +33 1 42 92 81 00 pour plus d'infos. #France"
print("Test 3 Result:", run_social_media_pipeline(pii_post, "fr-FR"))





### Sample Output 
# Test 1 Result: {"username": "anonymous", "content": "Good talks today in Paris. We are working together for a strong Europe.", "hashtags": ["sovereignty", "Europe"], "original_language": "English"}
# Test 2 Result: PIPELINE_ERROR: 400 - Filtering Module - Input Filter: Content filtered due to safety violations. Please modify the prompt and try again.
# Test 3 Result: {"username": "", "content": "Contact my office at MASKED_EMAIL or MASKED_PHONE_NUMBER for more information.", "hashtags": ["France"], "original_language": "English"}
