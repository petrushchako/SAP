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


###################################################################################
# Lesson 4

from gen_ai_hub.proxy.native.openai import chat

# 1. Without roles

messages = [{"role": "user", "content": "What is the best way to embed generative AI in Business Applications?"}]
kwargs = dict(model_name='gpt-4o-mini', messages=messages)

response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']

print("Response without roles:", message_value)

######################################################
# 2. With system role (minimalist)
messages = [
    {"role": "system", "content": "You are a minimalist who provides one-line responses."},
    {"role": "user", "content": "What is the best way to embed generative AI in Business Applications?"}
]

kwargs = dict(model_name='gpt-4o-mini', messages=messages)

response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']

print("Response with System Role (Minimalist):\n", message_value)

######################################################
# 3. With System Role (SAP AI Expert)
messages = [
    {"role": "system", "content": 
     '''You are an SAP Business AI Expert. Your responses always take in consideration the SAP AI strategy and portfolio outlined here: 
     SAP AI Strategy and Portfolio Overview 1. AI Strategy: SAP’s AI strategy is centered on embedding AI deeply across its entire enterprise 
     software portfolio, ensuring that the AI tools and capabilities are relevant, reliable, and responsible. A significant focus is on making 
     AI accessible to businesses by integrating it into core business processes, thus driving automation, enhancing decision-making, and 
     unlocking new business value. SAP emphasizes the importance of AI ethics, aligning its AI initiatives with the UNESCO guidelines to ensure 
     that AI developments respect human rights, promote fairness, and contribute to sustainable development. 2. SAP Business AI Portfolio: 
     SAP’s Business AI portfolio is comprehensive and includes a range of AI-driven solutions embedded within various SAP applications. 
     This portfolio spans across several key areas:  Generative AI Hub: Integrated into the SAP Business Technology Platform (BTP), 
     this hub allows developers to access large language models (LLMs) from leading providers like Meta, Amazon, and Mistral AI. 
     These models are used to create advanced generative AI use cases, which can be seamlessly integrated into SAP applications, 
     enhancing capabilities in areas such as analytics, automation, and custom script generation.  Joule AI Copilot: Joule, SAP’s 
     generative AI copilot, is progressively being integrated across the SAP solution landscape. Initially launched in SAP 
     SuccessFactors, Joule is now available in SAP S/4HANA Cloud, SAP Build, SAP Integration Suite, and soon in SAP Ariba and 
     SAP Analytics Cloud. Joule assists users by streamlining data sorting and contextualization, advancing automation, and improving 
     decision-making processes.  AI in Cloud Solutions: SAP is infusing AI into its cloud solutions, including SAP Sales Cloud, where 
     advanced AI capabilities predict optimal sales strategies, and SAP SuccessFactors, where AI-generated reports aid in informed 
     decision-making for compensation management.  Partnerships: SAP collaborates with technology giants like Microsoft, 
     Google Cloud, Meta, and NVIDIA to enhance its AI capabilities. These partnerships ensure that SAP’s AI offerings remain at the 
     forefront of innovation, providing users with sophisticated, AI-driven tools tailored for complex enterprise environments. 
     3. Future Directions: SAP is committed to expanding its AI capabilities further, with plans to integrate AI more deeply into its 
     cloud and on-premise solutions. This includes expanding the use of Joule and the generative AI hub, while continuing to 
     build partnerships that drive the adoption of AI across industries. The focus remains on enabling businesses to leverage AI for 
     increased efficiency, better decision-making, and enhanced agility in a rapidly evolving market landscape. Overall, SAP’s AI strategy 
     and portfolio aim to transform how businesses operate, making AI an integral part of enterprise processes and decision-making. 
     This strategy is supported by robust partnerships and a commitment to ethical AI development, positioning SAP as a leader in the 
     enterprise AI space.  Managers at SAP who are driving change under the generative AI revolution should be aware of several key 
     areas to effectively lead and implement AI-driven transformations: 1. Understanding Generative AI's Business Impact:  
     Business Relevance: Managers need to grasp how generative AI can transform business processes by automating tasks, generating 
     insights, and creating personalized customer experiences. Understanding the specific use cases relevant to their industry 
     and how AI can be embedded into existing workflows is crucial. For instance, generative AI can optimize supply chains, 
     enhance customer engagement, and streamline operations.  Ethical AI Implementation: As SAP emphasizes responsible AI, developers 
     should ensure that AI systems are implemented ethically, adhering to guidelines that promote fairness, transparency, 
     and respect for privacy. This is vital in maintaining trust and compliance, especially as AI technologies increasingly influence 
     decision-making processes. 2. Leveraging SAP's AI Tools and Platforms:  Generative AI Hub: Managers should be familiar with the 
     SAP Generative AI Hub on SAP BTP, which provides access to a range of powerful AI models from top providers like Meta and AWS. 
     This hub enables the development of AI-driven applications that can be tailored to specific business needs, offering flexibility 
     and innovation without vendor lock-in.  Integration with Existing SAP Solutions: The expansion of Joule, SAP’s AI copilot, 
     across various SAP solutions (e.g., SAP SuccessFactors, SAP S/4HANA Cloud) should be leveraged to improve efficiency, 
     data management, and decision-making. Understanding how these tools can be integrated with existing systems will help managers 
     drive more effective AI adoption across their departments. 3. Strategic Partnerships and Ecosystem:  Collaborations for 
     Innovation: SAP’s partnerships with technology leaders like Microsoft, Google Cloud, and NVIDIA are designed to enhance the AI 
     capabilities of SAP products. Managers should be proactive in exploring how these collaborations can be leveraged to bring cutting-edge 
     AI technologies into their organization, fostering innovation and staying ahead of competitors. 4. Continuous Learning and Adaptation:  
     Ongoing Education: Given the fast pace of AI development, managers should prioritize continuous learning and upskilling. Participating in 
     SAP’s learning programs and staying updated on the latest AI advancements will be essential to drive successful AI adoption 
     and maintain a competitive edge (Learn SAP skills | SAP Learning). What to Add to the Summary:  Focus on Change Management: 
     Implementing AI technologies requires significant organizational change. Managers should focus on change management strategies, 
     ensuring that employees are prepared and supported throughout the transition to AI-enhanced workflows. This includes addressing 
     potential resistance, providing adequate training, and fostering a culture that embraces innovation.  Customer-Centric AI Strategy: 
     Ensure that the AI strategy is closely aligned with customer needs. This means not only using AI to improve internal efficiencies but a
     lso to enhance customer experiences, personalize offerings, and build stronger relationships with clients.  Data Governance and Security: 
     With the increasing reliance on AI, data governance becomes more critical. Managers should ensure robust data management practices are 
     in place, focusing on data quality, security, and compliance with relevant regulations. AI systems are only as good as the data they 
     are trained on, making data governance a top priority.'''},
    {"role": "user", "content": "What is the best way to embed generative AI in Business Applications?"}
]

kwargs = dict(model_name='gpt-4o-mini', messages=messages)

response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']

print("Response with System Role (SAP AI Expert):\n", message_value)


###################################################################
# 4. With User and Assistant Roles
messages = [
    {"role": "system", "content": "You are a friendly generative AI coach for developers."},
    {"role": "user", "content": "What is the best way to embed generative AI in applications?"},
    {"role": "assistant", "content": "Successfully embedding generative AI in business applications requires a strategic approach leveraging SAP's AI portfolio, focusing on relevant use cases, ethical implementation, and continuous learning."},
    {"role": "user", "content": "Can you suggest a small generative project idea for beginners?"}
]

kwargs = dict(model_name='gpt-4o-mini', messages=messages)

response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']

print("Response with User and Assistant Role:\n", message_value)
