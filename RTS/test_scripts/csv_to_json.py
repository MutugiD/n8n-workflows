import csv
import json

input_csv = 'result.csv'
output_json = 'result.json'

# Read CSV
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

# Write JSON
with open(output_json, 'w', encoding='utf-8') as jsonfile:
    json.dump(data, jsonfile, indent=2, ensure_ascii=False)

# Print a sample of the output
print(f"Saved {len(data)} records to {output_json}.")
print("Sample record:")
if data:
    print(json.dumps(data[0], indent=2, ensure_ascii=False))