import json
import openai
import re

OPENAI_API_KEY = ''
openai.api_key = OPENAI_API_KEY

# Refined prompt for GPT
PROMPT_TEMPLATE = '''You are an expert B2B sales strategist. For each input, you will receive a JSON object containing a prospect's plan, including summary, key signals, and a recommended contact plan.\n\nYour task:\n- Synthesize this information to generate a concise, actionable outreach strategy.\n- The output should be only the recommended approach for outreach (the contact strategy), not a summary or key signals.\n- Do NOT simply repeat or rephrase the input fields. Instead, combine the information to create a unique, actionable plan.\n- If any information is missing, use only what is available.\n- Return only the recommended outreach approach as plain text, no JSON, no explanation, no markdown.\n\nInput:\n{input_json}\n'''

def extract_json_from_output(output_str):
    # Remove markdown if present
    if output_str.strip().startswith('```json'):
        output_str = output_str.strip().lstrip('```json').rstrip('```').strip()
    elif output_str.strip().startswith('```'):
        output_str = output_str.strip().lstrip('```').rstrip('```').strip()
    # Try to find the JSON object
    match = re.search(r'\{[\s\S]*\}', output_str)
    if match:
        return json.loads(match.group(0))
    else:
        return json.loads(output_str)

def main():
    with open('result_from_contact_agent.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        output_field = entry['output']
        try:
            contact_json = extract_json_from_output(output_field)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            continue
        name = contact_json.get('name', 'Unknown')
        # Compose the prompt
        prompt = PROMPT_TEMPLATE.format(input_json=json.dumps(contact_json, ensure_ascii=False, indent=2))
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        contact_strategy = response.choices[0].message.content.strip()
        print(f"{name}: {contact_strategy}\n")

if __name__ == "__main__":
    main()