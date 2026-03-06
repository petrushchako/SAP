# Controlling and Customizing LLM Behavior

### LLM Applications: Controlling Behaviour with System Prompts
Large Language Models (LLMs) like GPT are trained to predict the next word in a sentence based on context. To make their responses more useful and aligned with user expectations, we can structure conversations using roles and prompts to guide the model's behavior. One powerful way to do this is through the system prompt.

### Why Use a System Prompt?
A system prompt provides guidance to the model on how to behave in a conversation. It defines the role and context of the assistant, ensuring consistency and alignment with user expectations. Without a system prompt, the model may behave unpredictably or provide responses that lack clarity or focus.

<br><br><br>

### Understanding Roles in the chat.completions() API
When working with the chat.completions() API, three primary roles need to be defined to structure the interaction between the user and the assistant.

> Note: The init_llm function we used above allows easy initialization of LangChain model interfaces in a harmonized way via the SAP Cloud SDK. However, Chat.completions (equivalent to openai.ChatCompletions) may not work with some model families.

### 1. System Role
The system message is used to set up the behavior and personality of the assistant. This message guides how the assistant should act throughout the conversation. For example, you can specify:

  - "You are a friendly Python tutor"
  - "You are a helpful consultant for medical diagnosis"

Although this role helps define the assistant's tone and behavior, it is optional. Without a system message, the model will likely behave in a neutral and general way, similar to being instructed with a message like, "You are a helpful assistant."

### 2. Assistant Role
The assistant role represents the model itself. This is where the model generates responses based on the user's input and the instructions provided.

### 3. User Role
The user role represents the person interacting with the assistant. Users provide input—whether it's a question, request, or command—which the assistant responds to.

Each of these roles plays an important part in creating a structured and meaningful conversation between the assistant and the user.

**Note: The difference might not seem dramatic in the small example below, but it is more pronounced in larger contexts or when working with complex conversational structures.**


<br>

#### 1. Without Roles

```python
from gen_ai_hub.proxy.native.openai import chat

# 1. Without roles
messages = [{"role": "user", "content": "What is the best way to embed generative AI in Business Applications?"}]
kwargs = dict(model_name='gpt-4o-mini', messages=messages)

response = chat.completions.create(**kwargs)
response_dict = response.model_dump()
message_value = response_dict['choices'][0]['message']['content']

print("Response without roles:", message_value)
```

```sh
Response without roles: Embedding generative AI in business applications can enhance efficiency, creativity, and decision-making. Here are some best practices for integrating generative AI effectively:
1. **Identify Use Cases**: Start by identifying specific business problems or opportunities where generative AI can add value. Common use cases include content generation, data analysis, customer support automation, personalized marketing, and product design.
2. **Choose the Right Model**: Select a generative AI model that fits your use case. Depending on your needs, you might opt for models focused on natural language processing (NLP), image generation, or multi-modal capabilities. Consider models like OpenAI's GPT, DALL-E for images, or others tailored to your sector.
3. **Data Management**: Ensure high-quality data for training and fine-tuning the model. This may involve curating datasets, ensuring diversity in training data, and maintaining data privacy and compliance with regulations like GDPR.
4. **Collaborative Tools**: Integrate generative AI into existing applications and workflows. For instance, leveraging APIs to connect AI capabilities with CRM systems, content management systems, or design tools can streamline processes and improve user experience.
5. **User-Centric Design**: Focus on the end-user experience. The AI tool should be intuitive and seamlessly integrated into existing workflows. Providing a user-friendly interface and accessibility features can help ensure higher adoption rates.
6. **Feedback Loop**: Establish mechanisms for collecting feedback from users. Continuous iteration based on user input can enhance AI performance and relevance, helping to refine algorithms and improve user satisfaction.
7. **Ethics and Governance**: Implement ethical guidelines and governance frameworks to mitigate risks associated with bias, misinformation, and privacy concerns. Regularly audit AI outputs for fairness and accuracy, and be transparent with users about the AI’s capabilities and limitations.
8. **Training and Education**: Invest in training your staff on how to use generative AI tools effectively. This can ensure users are equipped to leverage AI capabilities to their fullest potential and understand the insights generated by AI.
9. **Performance Metrics**: Define and monitor key performance indicators (KPIs) to evaluate the effectiveness of generative AI integration. Metrics could include productivity improvements, user satisfaction, cost reductions, and ROI.
10. **Scalability**: Plan for scalability to accommodate growth and evolving business needs. Ensure that your AI infrastructure can handle increased usage and deployment across different departments or business units.
11. **Security Considerations**: Ensure strong security measures are in place to protect sensitive data and AI-generated outputs. Regularly assess the security risks associated with the use of AI technologies.
By following these best practices, businesses can harness the power of generative AI effectively, driving innovation and operational excellence while addressing user needs and concerns.
```
<br>

#### 2. With System Role (minimalist)

```python
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
```
```sh
Response with System Role (Minimalist):
 Integrate AI APIs to enhance decision-making and automate tasks.
```

<br>

#### 3. With System Role (SAP AI expert)

```python
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
```

```sh
Response with System Role (SAP AI Expert):
 Embedding generative AI in business applications effectively involves several strategic steps that align with SAP's AI strategy and portfolio. Here’s a comprehensive approach:

1. **Identify Relevant Use Cases**: 
   - Start by understanding the specific business processes that can benefit from generative AI. This could include automating customer service responses, enhancing marketing strategies, optimizing supply chain operations, or personalizing customer experiences.
   - Prioritize use cases based on their potential impact on efficiency, decision-making, and customer satisfaction.

2. **Leverage the SAP Generative AI Hub**:
   - Utilize the SAP Generative AI Hub integrated within the SAP Business Technology Platform (BTP). This hub allows access to large language models (LLMs) from top providers, ensuring flexibility and innovation.
   - Develop tailored applications using these AI models to meet specific business needs without being locked into a single vendor.

3. **Integrate with Existing SAP Solutions**:
   - Use Joule, SAP’s generative AI copilot, to enhance various SAP applications like SAP S/4HANA Cloud, SAP SuccessFactors, and others. Joule assists in streamlining data management, contextualization, and automation of tasks.
   - Ensure smooth integration with existing workflows to enhance the usability of AI capabilities, thereby minimizing disruptions during the transition.

4. **Focus on Change Management**:
   - Implement a structured change management strategy to support employees through the transition to AI-enhanced workflows. Address potential resistance by providing clear communication about the benefits of generative AI.
   - Provide training and upskilling opportunities to ensure employees can effectively use new AI tools.

5. **Emphasize Ethical AI Implementation**:
   - Align with the ethical guidelines set forth by SAP and international standards, ensuring fairness, transparency, and respect for user privacy. This is essential for gaining stakeholder trust and compliance.
   - Regularly assess the AI systems to mitigate biases and ensure they contribute positively to business processes.

6. **Enhance Customer-Centric Strategies**:
   - Ensure that the integration of generative AI aligns with customer needs by enhancing user experiences, personalizing services, and building stronger relationships.
   - Leverage AI to analyze customer data and preferences, enabling more targeted marketing and improved customer relationship management.

7. **Implement Robust Data Governance**:
   - Establish strong data governance practices focusing on data quality, security, and compliance. This includes ensuring that the data used for training AI models is accurate and ethically sourced.
   - Regularly audit and refine data management practices to support the AI lifecycle and maintain the effectiveness of AI applications.

8. **Continuous Learning and Adaptation**:
   - Foster a culture of continuous learning by encouraging teams to stay updated on the latest advancements in AI. This could involve participating in SAP learning programs or industry workshops.
   - Regularly iterate and adapt generative AI applications based on user feedback and evolving business needs to maintain relevance and effectiveness.

By following these steps and leveraging SAP’s AI capabilities, organizations can effectively embed generative AI into their business applications, driving automation, enhancing decision-making, and unlocking new business value in a responsible and sustainable manner.
```

#### 4. With User and Assistant Role

```python
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
```

```sh
Response with User and Assistant Role:
 Absolutely! Here’s a simple yet fun generative AI project idea for beginners:

### Project Idea: Text-to-Story Generator

**Overview:**
Create a web application that generates short stories based on user-defined prompts. This project can help you understand the basics of natural language processing and generative AI.

**Technologies:**
- **Programming Language:** Python (for backend) or JavaScript (for frontend)
- **Framework:** Flask or Django for Python, or Node.js for JavaScript
- **Frontend:** HTML, CSS, and JavaScript (or a framework like React)
- **AI Model:** Use a pre-trained model like GPT-2 or GPT-3 via OpenAI's API, or Hugging Face's Transformers library.

**Steps to Build:**

1. **Set Up Your Environment:**
   - Choose your stack (Flask/Django or Node.js).
   - Set up a basic web server that serves a simple HTML form where users can enter a prompt.
```

<br><br><br>

## Understanding the Parameters That Shape LLM Responses
These parameters allow us to control the length, creativity, and focus of the model’s output. By adjusting them, we can fine-tune the behavior of the model to suit different tasks and use cases.

- **Max Tokens**: Controls the length of the response. Try setting it to different values like 10, 50, or 100.
- **Temperature**: Controls the randomness or creativity of the response.
  - 0.0: Deterministic and focused responses.
  - Higher values like 0.7-1.0: More creative and varied responses.
- **Top-p (Nucleus Sampling)**: Limits the model to conisder only the most probable tokens while generating responses.
  - Try 0.9 or 0.95 - Encourages diversity while maintaining relevance.
 
<br>

### 1. Controlling Response Length with 'max_tokens'
When working with Large Language Models (LLMs), one of the most important parameters is max_tokens.
This parameter sets the maximum number of tokens the model can generate in its response.

Why does this matter?
- **Too low**: The answer may be cut off mid-sentence and feel incomplete.
- **Too high**: The model may generate unnecessarily long responses, wasting compute and increasing cost.
- **Just right**: You get a complete, clear answer without overusing resources.

**How to choose max_tokens**
- Short responses (<30): Use for classification tasks, short answers, or quick confirmations.
- Medium responses (30–100): Use for FAQs, explanations, or short summaries.
- Long responses (100+): Use when you need detail — teaching, storytelling, or technical documentation.

> A good practice: start with a reasonable estimate (e.g., 100 tokens for explanations) and adjust based on the task.
Remember, tokens != words. One token is roughly ~4 characters in English, so 100 tokens is about 75 words.

#### Example 1: Adjusting `max_tokens`

```python
messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain the concept of embeddings in LLMs briefly."}
        ]

# Function to test different max_tokens values
def test_max_tokens(max_tokens):
    kwargs = dict(model_name='gpt-4o-mini', messages=messages, max_tokens=max_tokens)

    response = chat.completions.create(**kwargs)
    response_dict = response.model_dump()
    message_value = response_dict['choices'][0]['message']['content']
    print(f"Max Tokens: {max_tokens}")
    print("Response:", message_value)
    print("\n" + "-"*80 + "\n")

# Test with varying max_tokens values
test_max_tokens(max_tokens=10)   # Very short response
test_max_tokens(max_tokens=100)   # Moderate-length response
test_max_tokens(max_tokens=300)  # Longer response
```

```sh
Max Tokens: 10
Response: Embeddings in large language models (LLMs)

--------------------------------------------------------------------------------

Max Tokens: 100
Response: Embeddings in Large Language Models (LLMs) refer to the mathematical representations of words, phrases, or sentences as high-dimensional vectors in a continuous vector space. These embeddings capture semantic relationships and contextual meanings, allowing the model to understand and process language more effectively.

Key points about embeddings in LLMs:

1. **Vector Representation**: Each word or token is represented as a dense vector. The dimensions of these vectors encode various linguistic features and relationships.

2. **Contextual Information**: In

--------------------------------------------------------------------------------

Max Tokens: 300
Response: Embeddings in large language models (LLMs) are numerical representations of words, phrases, or even entire sentences, designed to capture their meanings in a continuous vector space. Each embedding is typically a high-dimensional vector where similar meanings are mapped to nearby points. 

The concept of embeddings allows LLMs to understand and process natural language effectively by transforming categorical data (like words) into a form that is usable for mathematical operations. This transformation helps the model to learn relationships, similarities, and context among words based on the data it has been trained on.

In essence, embeddings enable LLMs to interpret text in a way that captures semantic relationships and contextual information, which is crucial for tasks like language generation, sentiment analysis, and more.

--------------------------------------------------------------------------------
```

### 2. Adjusting `temperature`
The temperature parameter controls how creative or random the model’s responses are.

A low temperature (0.0) makes the model deterministic — it always gives the same, safe answer.
A medium temperature (0.7) adds some creativity while keeping the response coherent.
A high temperature (1.0 or above) produces very creative, diverse outputs, but with more randomness.

**Why is Temperature Important? Choosing the right temperature depends on your use case:**
- **Low values (0–0.3)**: Great for factual, repeatable answers like database queries or coding help.
- **Medium values (0.5–0.8)**: Best for creative tasks where you want variety but still need consistency.
- **High values (0.9+)**: Useful for brainstorming, story generation, or poetry — where uniqueness matters more than precision.

**Choosing the Right Temperature**
- If you want accuracy and reliability → set temperature close to 0.0.
- If you want varied but still meaningful outputs → try 0.5–0.8.
- If you want wild creativity → go for 0.9–1.0.

> Start with 0.7 as a balanced default for most creative tasks.


Let’s see how this works in practice with a simple example: asking the model to write a short poem about the moon.

```python
 # Example 2: Adjusting Temperature

messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": "Write a short poem about the moon."}
        ]

def test_temperature(temperature):
    kwargs = dict(model_name='gpt-4o-mini', messages=messages, max_tokens=50, temperature = temperature)

    response = chat.completions.create(**kwargs)
    response_dict = response.model_dump()
    message_value = response_dict['choices'][0]['message']['content']
    print(f"Temperature: {temperature}")
    print("Response:", message_value)
    print("\n" + "-"*80 + "\n")

# Test with varying temperature values
test_temperature(temperature=0.0)  # Deterministic response
test_temperature(temperature=0.7)  # Balanced creativity
test_temperature(temperature=1.0)  # High creativity and randomness
```

```sh
Temperature: 0.0
Response: In the velvet cloak of night,  
The moon hangs low, a silver light,  
Whispers secrets to the stars,  
Guiding dreams from near to far.  

A lantern in the darkened sky,  
With craters deep and a

--------------------------------------------------------------------------------

Temperature: 0.7
Response: In the velvet sky, a silver gleam,  
The moon whispers softly, like a dream.  
A lantern aloft in the night’s embrace,  
Casting shadows with delicate grace.  

She dances on waves, a shimmering light,  
Guid

--------------------------------------------------------------------------------

Temperature: 1.0
Response: In the velvet sky, so high and bright,  
A silver jewel drapes the world in light.  
Whispers of dreams in her gentle glow,  
Night's silent guardian, soft and low.  

Waves of the ocean, drawn by

--------------------------------------------------------------------------------
```
<br>

### 3. Adjusting `top-p`
The top-p parameter, also called nucleus sampling, controls how much of the probability distribution is considered when generating the next token.

- At top-p = 1.0, the model considers the full probability distribution — from very likely to very unlikely words.
- At lower top-p values (e.g., 0.9, 0.5, 0.1), the model only samples from the most likely tokens, cutting off the tail of the distribution.

This makes responses more focused and less random.

**Why is Top-p Important? Choosing the right top-p is useful when:**
- You want focused and coherent outputs → set a lower top-p.
- You want variety but still within reason → keep top-p higher, around 0.8–1.0.

#### Practical Use Cases (Top-p)
- Top-p = 1.0: Best for open-ended, artistic, or exploratory tasks where creativity is paramount (e.g., writing poetry, brainstorming ideas).
- Top-p = 0.9: Suitable for tasks requiring creativity with a touch of control, like marketing content or user-facing explanations.
- Top-p = 0.5: Good for structured and semi-creative content, such as professional writing or concise presentations.
- Top-p = 0.1: Perfect for scenarios demanding high accuracy and low randomness, like generating factual summaries or code snippets.



```python
 # Example 3: Adjusting Top-p


# Define the input messages
messages = [
    {"role": "system", "content": "You are a dungeon master in a fantasy roleplay game."},
    {"role": "user", "content": "The player enters a dark cave. Describe what happens next."}
]

# Function to test different top-p values
def test_top_p(top_p):
    kwargs = dict(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=100,  # Keep responses concise
        temperature=0.7,  # Adds some randomness
        top_p=top_p  # Nucleus sampling
    )
    response = chat.completions.create(**kwargs)
    response_dict = response.model_dump()
    message_value = response_dict['choices'][0]['message']['content']
    print(f"Top-p: {top_p}")
    print("Response:", message_value)
    print("\n" + "-"*80 + "\n")

# Test significant changes in top-p values
test_top_p(top_p=1.0)  # Full range of probabilities
test_top_p(top_p=0.9)  # Limits to the most probable tokens
test_top_p(top_p=0.5)  # Further restricts probabilities
test_top_p(top_p=0.1)  # Highly focused on top-probability tokens
```

```sh
Top-p: 1.0
Response: As you step into the dark cave, the air grows noticeably cooler and carries a damp, earthy scent. The sound of dripping water echoes softly in the distance, and the faint rustle of something unseen sends a shiver down your spine. 

Your eyes slowly adjust to the dim light filtering in from the entrance, revealing rough stone walls adorned with patches of luminous moss that cast an eerie green glow. Shadows dance around you, creating the illusion of movement just beyond your sight.

Ahead, you notice the

--------------------------------------------------------------------------------

Top-p: 0.9
Response: As you step into the dark cave, the cool air wraps around you like a damp cloak, and the faint sound of dripping water echoes in the distance. Your eyes slowly adjust to the dim light, revealing rough-hewn stone walls that glisten with moisture. Shadows dance along the ground, cast by the flickering light of your torch.

The narrow passage leads deeper into the cave, and you can feel a slight breeze flowing through, carrying with it a faint, earthy scent. As you move further

--------------------------------------------------------------------------------

Top-p: 0.5
Response: As you step into the dark cave, the air grows noticeably cooler, and a damp, earthy scent fills your nostrils. The faint sound of dripping water echoes off the stone walls, creating an eerie symphony that reverberates through the stillness. Your eyes slowly adjust to the dim light, revealing jagged rock formations that jut out from the walls like the teeth of some ancient beast.

Ahead, the cave narrows into a winding passage, with shadows dancing at the edges of your vision

--------------------------------------------------------------------------------

Top-p: 0.1
Response: As you step into the dark cave, the air grows noticeably cooler, and a damp chill wraps around you like a shroud. The faint sound of dripping water echoes in the distance, creating an eerie rhythm that seems to pulse with the heartbeat of the cave itself. Your footsteps crunch softly on the gravelly floor, and the darkness swallows the light from your torch, casting long, flickering shadows on the rough stone walls.

As your eyes adjust, you notice faint glimmers of moisture on the

--------------------------------------------------------------------------------
```
<br>

#### Temperature vs. Top-p in Practice
Temperature controls randomness in how tokens are picked.
Example: At high temperature, the same cave could be described with very unusual or artistic phrasing.

Top-p controls breadth of choices.
Example: At medium top-p, the cave might contain bats, treasure, or a sleeping monster. At very low top-p, it might always just be “dark and empty.”

#### Adjusting Temperature and Top-p Together
The best practice is to adjust either temperature or top-p, not both at the same time.
- Changing both parameters can skew the token probability distribution too drastically, making behavior unpredictable or hard to interpret.
- If you want more creativity or randomness, increase temperature from its default (e.g., to ~0.7–0.9).
- If you want to filter token candidates based on probability mass, adjust top-p (e.g., between 0.8–0.9).
