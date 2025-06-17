import csv
import openai
import os
import time

# User must set their OpenAI API key as a string (for testing purposes)
OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

RESULT_CSV = 'result.csv'
RTS_CSV = 'RTS-TEST-DATA - Sheet1.csv'
OUTPUT_CSV = 'RTS-TEST-DATA - Sheet1.enriched.csv'
DEBUG_LOG = 'debug_gpt4o_batch.log'

def normalize_url(url):
    if not url:
        return ''
    url = url.strip().rstrip('/').lower()
    url = url.replace('www.', '')
    return url

# Read result.csv into a dict by normalized linkedinProfileUrl
profiles = {}
with open(RESULT_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    result_rows = list(reader)
    for row in result_rows:
        url = row.get('linkedinProfileUrl')
        if url:
            profiles[normalize_url(url)] = row
print(f"[INFO] Read {len(result_rows)} rows from result.csv.")

# Read RTS-TEST-DATA - Sheet1.csv
with open(RTS_CSV, newline='', encoding='utf-8') as f:
    rts_rows = list(csv.reader(f))
print(f"[INFO] Read {len(rts_rows)-1} data rows from RTS-TEST-DATA - Sheet1.csv.")

header = rts_rows[0]
# Rename/add new columns
for col in ['Extracted Email', 'Extracted Phone Number', 'Extracted Contact']:
    if col not in header:
        header.append(col)

# Prepare to update rows
updated_rows = [header]

with open(DEBUG_LOG, 'w', encoding='utf-8') as debug_log:
    debug_log.write(f"[INFO] Read {len(result_rows)} rows from result.csv.\n")
    debug_log.write(f"[INFO] Read {len(rts_rows)-1} data rows from RTS-TEST-DATA - Sheet1.csv.\n")
    debug_log.write("[INFO] Entering main processing loop.\n")
    print("[INFO] Entering main processing loop.")
    # Log all linkedin_url values and all profile keys
    debug_log.write("[DEBUG] All linkedin_url values from master sheet:\n")
    for row in rts_rows[1:]:
        debug_log.write(f"{row[0]}\n")
    debug_log.write("[DEBUG] All normalized profile keys from result.csv:\n")
    for k in profiles.keys():
        debug_log.write(f"{k}\n")
    if len(rts_rows) <= 1:
        debug_log.write("[WARNING] No data rows to process in RTS-TEST-DATA - Sheet1.csv. Exiting.\n")
        print("[WARNING] No data rows to process in RTS-TEST-DATA - Sheet1.csv. Exiting.")
    for row in rts_rows[1:]:
        # Find LinkedIn URL
        try:
            linkedin_url = row[0].strip()
        except IndexError:
            updated_rows.append(row)
            continue
        norm_url = normalize_url(linkedin_url)
        profile = profiles.get(norm_url)
        if not profile:
            debug_log.write(f"[WARNING] No profile match for {linkedin_url} (normalized: {norm_url})\n")
            updated_rows.append(row)
            continue
        # Concatenate fields
        text = '\n'.join([
            profile.get('linkedinDescription', ''),
            profile.get('linkedinJobDescription', ''),
            profile.get('linkedinHeadline', '')
        ])
        debug_log.write(f"\n[DEBUG] Profile text for {linkedin_url}:\n{text}\n---\n")
        print(f"\n[DEBUG] Profile text for {linkedin_url}:\n{text}\n---")
        if not text.strip():
            debug_log.write(f"[WARNING] No profile text for {linkedin_url}, skipping GPT call.\n")
            print(f"[WARNING] No profile text for {linkedin_url}, skipping GPT call.")
            contacts = {"email": "", "phone_number": "", "contact": ""}
            while len(row) < len(header):
                row.append('')
            row[header.index('Extracted Email')] = contacts.get('email', '')
            row[header.index('Extracted Phone Number')] = contacts.get('phone_number', '')
            row[header.index('Extracted Contact')] = contacts.get('contact', '')
            updated_rows.append(row)
            continue
        prompt = f"""
You are an expert at extracting contact information from text.
Given the following LinkedIn profile data, extract:
- All email addresses (including obfuscated ones like 'name [at] domain dot com' or 'name(at)domain(dot)com')
- All phone numbers (in any format)
- Any other direct contact information (Telegram, WhatsApp, etc.)

Respond ONLY with a JSON object, no markdown, no explanation, no code block. Use these keys: "email", "phone_number", "contact". If nothing is found, use empty strings.

Example output:
{{"email": "john.doe@gmail.com", "phone_number": "+1-555-123-4567", "contact": "Telegram: @johndoe"}}

Profile Data:
{text}
"""
        # Call GPT-4o
        try:
            debug_log.write(f"\nPrompt for {linkedin_url}:\n{prompt}\n---\n")
            print(f"\nPrompt for {linkedin_url}:\n{prompt}\n---")
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            content = response.choices[0].message.content
            debug_log.write(f"Response for {linkedin_url}:\n{content}\n---\n")
            print(f"Response for {linkedin_url}:\n{content}\n---")
            # Strip markdown/code block formatting
            content = content.strip()
            if content.startswith('```'):
                content = content.strip('`')
                content = content.replace('json', '').strip()
            # Try to parse JSON from response
            import json
            import re
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                contacts = json.loads(match.group(0))
            else:
                debug_log.write(f"[ERROR] Could not parse JSON for {linkedin_url}. Raw response:\n{content}\n---\n")
                print(f"[ERROR] Could not parse JSON for {linkedin_url}. Raw response:\n{content}\n---")
                contacts = {"email": "", "phone_number": "", "contact": ""}
        except Exception as e:
            debug_log.write(f"Error for {linkedin_url}: {e}\n")
            print(f"Error for {linkedin_url}: {e}")
            contacts = {"email": "", "phone_number": "", "contact": ""}
        # Append to row
        while len(row) < len(header):
            row.append('')
        row[header.index('Extracted Email')] = contacts.get('email', '')
        row[header.index('Extracted Phone Number')] = contacts.get('phone_number', '')
        row[header.index('Extracted Contact')] = contacts.get('contact', '')
        updated_rows.append(row)
        time.sleep(2)  # Add delay to avoid rate limits

# Write updated CSV
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(updated_rows)

print(f"Enrichment complete. Results saved to {OUTPUT_CSV}")


'''
You are an expert at extracting contact information from text.

Given the following LinkedIn profile data, extract and output:
- The first email address you find (including obfuscated ones like 'name [at] domain dot com' or 'name(at)domain(dot)com'), converted to standard format.
- The first phone number you find (in any format).
- The first other direct contact information you find (such as Telegram, WhatsApp, etc.).

Output ONLY the following three fields, separated by commas, in this order:
email, phone_number, contact

If any field is not found, leave it blank but keep the commas.

Example output:
john.doe@gmail.com,+1-555-123-4567,Telegram: @johndoe

Another example (if only email is found):
jane.smith@email.com,,

Another example (if nothing is found):
,,

Here is the LinkedIn profile data:
[Paste the profile data here]

'''