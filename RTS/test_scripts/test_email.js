const fs = require('fs');

// Read the JSON file
const inputFile = 'email_added.json';
const rawData = fs.readFileSync(inputFile);
const jsonData = JSON.parse(rawData);

// The user's script expects data in the format which is an array of items,
// where each item has a 'json' property.
// We need to wrap our data in this structure.
const input = jsonData.map(item => ({ json: item }));

// User's script
const result = input.map(item => {
  const apolloEmail = item.json['Apollo enrichment'] || '';
  return {
    json: {
      ...item.json,
      email_added: apolloEmail.trim() !== '' ? 'Available' : ''
    }
  };
});

// Print the result to console
console.log(JSON.stringify(result, null, 2));
