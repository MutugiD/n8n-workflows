// Google Sheet: https://docs.google.com/spreadsheets/d/1rVJ5HADiC0OembrsvKyfvbck7kVCWIATf37Fb7o_dLI/edit?gid=0#gid=0

function normalizeLinkedinUrl(url) {
  if (!url) return '';
  let normalized = url.trim();
  // Add www if missing
  normalized = normalized.replace(/^https:\/\/linkedin\.com/, 'https://www.linkedin.com');
  // Add trailing slash if missing
  if (!normalized.endsWith('/')) normalized += '/';
  return normalized;
}

return $input.all().map(item => {
  return {
    json: {
      linkedinProfileUrl: normalizeLinkedinUrl(item.json.linkedinProfileUrl),
      Domain: item.json.linkedinCompanyUrl || '',
      'Apollo enrichment': item.json.extractedEmail || ''
    }
  };
});