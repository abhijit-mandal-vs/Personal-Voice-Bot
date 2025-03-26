import json
from collections import defaultdict

def validate_dataset(file_path):
    stats = defaultdict(int)
    with open(file_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            stats['total_examples'] += 1
            if len(entry['messages']) != 3:
                stats['invalid_structure'] += 1
            if not entry['messages'][2]['content'].strip():
                stats['empty_responses'] += 1
    
    print(f"Validation Results for {file_path}:")
    print(f"Total examples: {stats['total_examples']}")
    print(f"Invalid structure: {stats['invalid_structure']}")
    print(f"Empty responses: {stats['empty_responses']}")

if __name__ == "__main__":
    validate_dataset('data/personal_responses.jsonl')