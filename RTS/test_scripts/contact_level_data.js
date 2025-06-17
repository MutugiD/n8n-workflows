// n8n Code node: Extract contact-level data from enriched profile

const contactFields = [
  'firstName',
  'lastName',
  'extractedEmail',
  'extractedContact',
  'profileUrl',
  'linkedinProfileUrl',
  'linkedinHeadline',
  'linkedinJobTitle',
  'linkedinJobDescription',
  'linkedinJobLocation',
  'linkedinConnectionsCount',
  'linkedinSkillsLabel',
  'location'
];

const items = $input.all();
const contactItems = items.map(item => {
  const profile = item.json;
  const contactData = {};
  for (const field of contactFields) {
    if (profile[field] !== undefined) {
      contactData[field] = profile[field];
    }
  }
  return { json: contactData };
});

return contactItems;