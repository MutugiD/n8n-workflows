// This code runs in n8n code block
// Input: items[0].json contains the profile data
// Output: items[0].json with added contact fields

const OPENAI_API_KEY = '';

// Helper function to robustly normalize email obfuscations
function normalizeObfuscatedEmails(text) {
  return text
    // Replace various [at], (at), {at}, at, AT, etc. with @
    .replace(/\s*\[at\]|\(at\)|\{at\}|\sat\s|\sat\.|\sat,|\sat\b|\sAT\s|\sAT\.|\sAT,|\sAT\b/gi, '@')
    // Replace various [dot], (dot), {dot}, dot, DOT, etc. with .
    .replace(/\s*\[dot\]|\(dot\)|\{dot\}|\sdot\s|\sdot\.|\sdot,|\sdot\b|\sDOT\s|\sDOT\.|\sDOT,|\sDOT\b/gi, '.')
    // Replace obfuscated at and dot with @ and .
    .replace(/\s+at\s+/gi, '@')
    .replace(/\s+dot\s+/gi, '.')
    // Remove spaces around @ and .
    .replace(/\s*@\s*/g, '@')
    .replace(/\s*\.\s*/g, '.')
    // Remove any trailing punctuation after email parts
    .replace(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)\.+/g, '$1.');
}

function extractEmails(text) {
  const normalized = normalizeObfuscatedEmails(text);
  // Extract emails using regex
  const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const emails = normalized.match(emailRegex) || [];
  return emails.map(email => email.trim()).filter(email => email.includes('@') && email.includes('.'));
}

// Helper function to extract phone numbers
function extractPhones(text) {
  const phoneRegex = /(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g;
  return text.match(phoneRegex) || [];
}

async function extractContacts(profile) {
  // Combine relevant text fields
  const text = [
    profile.linkedinDescription || '',
    profile.linkedinJobDescription || '',
    profile.linkedinHeadline || ''
  ].join('\n');

  // Extract using regex first
  const emails = extractEmails(text);
  const phones = extractPhones(text);

  // If we found emails, return them immediately
  if (emails.length > 0) {
    return {
      extractedEmail: emails[0],
      extractedPhoneNumber: phones[0] || '',
      extractedContact: emails.join('; ')
    };
  }

  // If no emails found, try GPT-4o for any other contact info
  const prompt = `Extract contact information from this LinkedIn profile text. Return ONLY a JSON object with these fields:\n{\n  "email": "extracted email or empty string",\n  "phone": "extracted phone or empty string",\n  "other_contact": "any other contact info or empty string"\n}\n\nText: ${text}`;

  try {
    const response = await $http.post({
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.1
      })
    });
    const result = JSON.parse(response.body.choices[0].message.content);
    return {
      extractedEmail: result.email || '',
      extractedPhoneNumber: result.phone || '',
      extractedContact: result.other_contact || ''
    };
  } catch (error) {
    return {
      extractedEmail: '',
      extractedPhoneNumber: '',
      extractedContact: ''
    };
  }
}

// Process all input items
const items = $input.all();
const enrichedItems = [];

for (const item of items) {
  const profile = item.json;
  if (!profile) {
    enrichedItems.push(item);
    continue;
  }
  const contacts = await extractContacts(profile);
  enrichedItems.push({
    json: {
      ...profile,
      ...contacts
    }
  });
}

return enrichedItems;