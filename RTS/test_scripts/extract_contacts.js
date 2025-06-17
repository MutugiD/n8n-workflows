const fs = require('fs');
const axios = require('axios');

console.log('Script started');
console.log('Current working directory:', process.cwd());

const OPENAI_API_KEY = '';

async function extractContacts(text) {
  const prompt = `
You are an expert at extracting contact information from text.
Given the following LinkedIn profile data, extract:
- All email addresses (including obfuscated ones like 'name [at] domain dot com' or 'name(at)domain(dot)com')
- All phone numbers (in any format)
- Any other direct contact information (Telegram, WhatsApp, etc.)

Respond ONLY with a JSON object, no markdown, no explanation, no code block. Use these keys: "email", "phone_number", "contact". If nothing is found, use empty strings.

Example output:
{"email": "john.doe@gmail.com", "phone_number": "+1-555-123-4567", "contact": "Telegram: @johndoe"}

Profile Data:
${text}
`;

  console.log('---\nPrompt sent to GPT-4o:\n', prompt);

  try {
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    let content = response.data.choices[0].message.content.trim();
    console.log('Raw GPT-4o response:\n', content);
    // Remove markdown/code block if present
    if (content.startsWith('```')) {
      content = content.replace(/```[a-z]*\n?/i, '').replace(/```$/, '').trim();
    }
    // Extract JSON
    let contacts = { email: '', phone_number: '', contact: '' };
    try {
      const match = content.match(/\{[\s\S]*\}/);
      if (match) {
        contacts = JSON.parse(match[0]);
      }
    } catch (e) {
      console.log('JSON parse error:', e);
    }
    return contacts;
  } catch (err) {
    console.error('OpenAI API error:', err.response ? err.response.data : err.message);
    return { email: '', phone_number: '', contact: '' };
  }
}

async function main() {
  let data;
  try {
    if (!fs.existsSync('result.json')) {
      console.error('result.json does not exist!');
      return;
    }
    data = JSON.parse(fs.readFileSync('result.json', 'utf-8'));
  } catch (e) {
    console.error('Failed to read result.json:', e);
    return;
  }
  console.log(`[INFO] Loaded ${data.length} profiles from result.json.`);
  let found = false;
  for (const profile of data) {
    const text = [
      profile.linkedinDescription || '',
      profile.linkedinJobDescription || '',
      profile.linkedinHeadline || ''
    ].join('\n');
    console.log('\n[INFO] Processing profile:', profile.linkedinProfileUrl || profile.profileUrl);
    const contacts = await extractContacts(text);
    console.log('Extracted:', contacts);
    if (contacts.email || contacts.phone_number || contacts.contact) {
      found = true;
      break; // Stop after first successful extraction
    }
    // Wait to avoid rate limits
    await new Promise(res => setTimeout(res, 2000));
  }
  if (!found) {
    console.log('No contacts extracted from any profile.');
  }
}

(async () => {
  try {
    await main();
  } catch (e) {
    console.error('Uncaught error:', e);
  }
})();