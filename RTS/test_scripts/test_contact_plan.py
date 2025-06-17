import json
import openai
import os

# Set your OpenAI API key
OPENAI_API_KEY = ''
openai.api_key = OPENAI_API_KEY
def load_contact_data():
    with open('contact_level_data.json', 'r') as f:
        return json.load(f)

def generate_contact_plan(contact):
    prompt = f"""You are an expert B2B sales research assistant. Given the following contact-level LinkedIn data, generate a concise, actionable summary for a sales prospecting plan.

Relevant Contact Data:
{contact['firstName']} {contact['lastName']}
Email: {contact['extractedEmail']}
LinkedIn: {contact['profileUrl']}
Headline: {contact['linkedinHeadline']}
Job Title: {contact['linkedinJobTitle']}
Job Description: {contact['linkedinJobDescription']}
Skills: {contact['linkedinSkillsLabel']}
Location: {contact['location']}

Instructions:
- Generate ONLY the contact plan section
- Focus on actionable insights and specific outreach recommendations
- Keep the contact plan concise and relevant to their role/industry
- Only include information that is present or can be reasonably inferred from the data

Format your response EXACTLY as follows, with no additional text or formatting:
{{
  "linkedinProfileUrl": "{contact['profileUrl']}",
  "ContactPlan": "A single paragraph with specific, actionable outreach recommendations based on their role, experience, and potential needs. Focus on how to approach them and what value to offer."
}}"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

def main():
    contacts = load_contact_data()
    results = []

    for contact in contacts:
        if contact['firstName'] and contact['lastName']:  # Skip empty entries
            try:
                contact_plan = generate_contact_plan(contact)
                results.append(contact_plan)
            except Exception as e:
                print(f"Error processing {contact['firstName']} {contact['lastName']}: {str(e)}")

    # Combine all results into a single JSON array
    combined_results = "[\n" + ",\n".join(results) + "\n]"

    # Save results to file
    with open('contact_plans.json', 'w') as f:
        f.write(combined_results)

    print("Contact plans generated and saved to contact_plans.json")

if __name__ == "__main__":
    main()