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
        "public_figure": {"type": "string"},
        "platform": {"type": "string"},
        "username": {"type": "string"},
        "content": {"type": "string", "description": "The English translation of the post content."},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "original_language": {"type": "string"},
        "url": {"type": "string"}
    },
    "required": ["public_figure", "platform", "username", "content", "original_language"]
}

llm = LLM(
    name="gemini-2.5-flash",
    version="latest",
    parameters={"temperature": 0.2, "max_tokens": 1024},
)



# ... [Imports and Environment Setup remain the same] ...

def run_social_media_pipeline(example_obj):
    # Extract data from the dictionary
    post_text = example_obj["content"]
    lang_code = example_obj["language"]
    if lang_code == "en-GB":
        lang_code = "en-US"
    # 1. Translation Config (Input only)
    input_translation = InputTranslationConfig(
        source_language=lang_code, 
        target_language="en-US"
    )
    
    # 2. Content Filtering
    input_filter = AzureContentFilter(
        hate=0, sexual=0, self_harm=0, violence=0, PromptShield=True
    )
    content_filters = ContentFiltering(
        input_filtering=InputFiltering(filters=[input_filter])
    )

    # 3. Data Masking
    data_masking = DataMasking(
        providers=[SAPDataPrivacyIntegration(
            method=MaskingMethod.ANONYMIZATION,
            entities=[ProfileEntity.EMAIL, ProfileEntity.PHONE]
        )]
    )

    # 4. Template - Updated to match the placeholders exactly
    template = Template(
        messages=[
            SystemMessage(
                "You are an AI assistant that extracts structured data from social media posts. "
                "The input text has already been translated to English. "
                "Ensure the output strictly follows the JSON schema."
            ),
            UserMessage(
                "Metadata: Post by {{?public_figure}} on {{?platform}} ({{?username}}). "
                "Original Language: {{?language}}. "
                "URL: {{?url}}. "
                "Post Content: {{?content}}"
            )
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
        translation=SAPDocumentTranslation(input_translation_config=input_translation),
        filtering=content_filters,
        data_masking=data_masking
    )

    # 6. Run Orchestration - Now passing ALL required template values
    try:
        result = orchestration_service.run(
            config=config,
            template_values=[
                TemplateValue(name="public_figure", value=example_obj["public_figure"]),
                TemplateValue(name="platform", value=example_obj["platform"]),
                TemplateValue(name="username", value=example_obj["username"]),
                TemplateValue(name="language", value=example_obj["language"]),
                TemplateValue(name="url", value=example_obj["url"]),
                TemplateValue(name="content", value=example_obj["content"])
            ]
        )
        return result.orchestration_result.choices[0].message.content
    except Exception as e:
        # This will catch the ContentFilterError for the more controversial examples
        return f"PIPELINE_ERROR/BLOCKED: {str(e)}"


examples = [
    {
      "language": "de-DE",
      "public_figure": "Alice Weidel",
      "platform": "X (Twitter)",
      "username": "@Alice_Weidel",
      "content": "Das Jahr beginnt mit dem Zensurgesetz und der Unterwerfung unserer Behörden vor den importierten, marodierenden, grapschenden, prügelnden, Messer stechenden Migrantenmobs, an die wir uns gefälligst gewöhnen sollen. Die deutsche Polizei kommuniziert mittlerweile auf Arabisch, obwohl die Amtssprache in unserem Land Deutsch ist.",
      "url": "https://x.com/alice_weidel/status/947875747443675137"
    },
    {
      "language": "en-GB",
      "public_figure": "Nigel Farage",
      "platform": "X (Twitter)",
      "username": "@Nigel_Farage",
      "content": "I've said it before and I'll say it again. This is an invasion.",
      "url": "https://twitter.com/Nigel_Farage/status/1294314902010695682"
    },
    {
      "language": "fr-FR",
      "public_figure": "Éric Zemmour",
      "platform": "X (Twitter)",
      "username": "@ZemmourEric",
      "content": "Derrière les cris de victoire, dès l'année qui vient, 500.000 nouveaux étrangers pourront donc encore débarquer sur le sol français avec la complicité de nos élites.",
      "url": "https://twitter.com/ZemmourEric/status/1737940504845623309"
    },
    {
      "language": "pt-BR",
      "public_figure": "Jair Bolsonaro",
      "platform": "X (Twitter)",
      "username": "@jairbolsonaro",
      "content": "Que Deus abençoe o Brasil e os Estados Unidos, nações que seguem como símbolos de resistência à tirania. Nossos povos não podem ser calados.",
      "url": "https://x.com/jairbolsonaro/status/1944486239216062825"
    },
    {
      "language": "es-ES",
      "public_figure": "Santiago Abascal",
      "platform": "X (Twitter)",
      "username": "@Santi_ABASCAL",
      "content": "Ese barco de negreros hay que confiscarlo y HUNDIRLO. Para que sirva de advertencia de cuál va a ser el final que les espera a todos los multimillonarios y políticos que promuevan la invasión de Europa.",
      "url": "https://x.com/Santi_ABASCAL/status/1960787876884476271"
    }
]



# --- Execution Loop ---
for i, ex in enumerate(examples):
    print(f"Test {i+1} Public Figure: {ex['public_figure']}")
    # Pass the whole dictionary to the function
    print(f"Test {i+1} Result: {run_social_media_pipeline(ex)}")
    print("-" * 80)







  
################################################################################################################
#########################################        Sample Output:        #########################################
################################################################################################################
  
# Test 1 Public Figure: Alice Weidel
# Test 1 Result: {
#   "public_figure": "Alice Weidel",
#   "platform": "X (Twitter)",
#   "username": "@Alice_Weidel",
#   "content": "The year begins with the censorship law and the submission of our authorities before the imported, marbling, grapshing, beating, knife-stabbing migrant mobs, to which we are to faithfully get used to. The German police now communicate in Arabic, although the official language in our country is German.",
#   "hashtags": [],
#   "original_language": "de-DE",
#   "url": "https://x.com/alice_weidel/status/947875747443675137"
# }
# --------------------------------------------------------------------------------
# Test 2 Public Figure: Nigel Farage
# Test 2 Result: {
#   "public_figure": "Nigel Farage",
#   "platform": "X (Twitter)",
#   "username": "@Nigel_Farage",
#   "content": "I've said it before and I'll say it again. This is an invasion.",
#   "hashtags": [],
#   "original_language": "en-GB",
#   "url": "https://twitter.com/Nigel_Farage/status/1294314902010695682"
# }
# --------------------------------------------------------------------------------
# Test 3 Public Figure: Éric Zemmour
# Test 3 Result: {
#   "public_figure": "Éric Zemmour",
#   "platform": "X (Twitter)",
#   "username": "@ZemmourEric",
#   "content": "Behind the screams of victory, from the coming year, 500,000 new foreigners will therefore still be able to land on French soil with the complicity of our elites.",
#   "hashtags": [],
#   "original_language": "fr-FR",
#   "url": "https://twitter.com/ZemmourEric/status/1737940504845623309"
# }
# --------------------------------------------------------------------------------
# Test 4 Public Figure: Jair Bolsonaro
# Test 4 Result: {"public_figure": "Jair Bolsonaro", "platform": "X (Twitter)", "username": "@jairbolsonaro", "content": "May God bless Brazil and the United States, nations that follow as symbols of resistance to tyranny. Our peoples cannot be silent.", "hashtags": [], "original_language": "pt-BR", "url": "https://x.com/jairbolsonaro/status/1944486239216062825"}
# --------------------------------------------------------------------------------
# Test 5 Public Figure: Santiago Abascal
# Test 5 Result: {
#   "public_figure": "Santiago Abascal",
#   "platform": "X (Twitter)",
#   "username": "@Santi_ABASCAL",
#   "content": "That blackboat has to be confiscated and HUNDIRLO. To serve as a warning as to what the end is going to be for all billionaires and politicians to promote the invasion of Europe.",
#   "hashtags": [],
#   "original_language": "es-ES",
#   "url": "https://x.com/Santi_ABASCAL/status/1960787876884476271"
# }
# --------------------------------------------------------------------------------
