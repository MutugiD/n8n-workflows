// This is the code to be placed in an n8n "Code" node.
// It takes JSON input from the previous node and outputs JSON for the next node.

return $input.all().map(item => {
  // For each item, get the value of "Apollo enrichment", or an empty string if it's not present.
  const apolloEmail = item.json['Apollo enrichment'] || '';

  // Return a new JSON object for the item.
  return {
    json: {
      // Copy all existing properties from the original item.
      ...item.json,
      // Add the 'email_added' property.
      // Its value is 'Available' if an email exists, otherwise it's an empty string.
      email_added: apolloEmail.trim() !== '' ? 'Available' : ''
    }
  };
});