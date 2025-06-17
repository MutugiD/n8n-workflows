import openai

OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

text = '''Hey there, I'm Shaun! I love being the bridge between engineers and everyone else and thrive in environments where soft skills are just as important as technical skills. I'm am an extreme power-user of products and I love to nerd out with APIs, Computer Vision, Salesforce, and all sorts of data.

Getting to use both my soft skills and technical skills on a regular basis is important to me. I genuinely enjoy managing and building teams and working with people from all backgrounds and experiences. Leveraging my technical experiences to improve processes and empower others is what gets me up in the morning.

I graduated from Iowa State University in 2016, where I received my B.S. in Software Engineering. During my academic career, I was able to do a full-time internship at 6 different amazing companies including Twilio, Microsoft, Amazon, Boeing, the MathWorks, and Union Pacific. During these internships, I gained great insight into what software engineering is all about and was able to pick up best practices from a wide variety of work environments.

LET'S CONNECT
Feel free to send me an email any time, shauntvanweelden [AT] gmail [DOT] com'''

prompt = f"""
You are an expert at extracting contact information from text.
Given the following LinkedIn profile data, extract:
- All email addresses (including obfuscated ones like 'name [at] domain dot com' or 'name(at)domain(dot)com')
- All phone numbers (in any format)
- Any other direct contact information (Telegram, WhatsApp, etc.)

Return ONLY a valid JSON object with these keys: "email", "phone_number", "contact". If nothing is found, use empty strings. Do not return any explanation or text outside the JSON object.

Example output:
"""
{"email": "john.doe@gmail.com", "phone_number": "+1-555-123-4567", "contact": "Telegram: @johndoe"}
"""

Profile Data:
"""
prompt += f"""
{text}
"""

print("Prompt:\n", prompt)

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)
content = response.choices[0].message.content
print("\nRaw GPT-4o response:\n", content)