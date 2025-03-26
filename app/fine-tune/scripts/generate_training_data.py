import os
import json


def create_training_entry(question, your_response):
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Respond exactly like [Your Name] would - using your typical phrases, sentence structures, and level of detail",
            },
            {"role": "user", "content": question},
            {"role": "assistant", "content": your_response},
        ]
    }


# Example usage
questions_and_answers = [
    ("What should we know about your life story?", "Your actual response here"),
    ("What's your #1 superpower?", "Your actual response here"),
    # Add more Q&A pairs
]

# Create data directory if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# Use the complete path for the output file
output_file = os.path.join(data_dir, "personal_responses.jsonl")

with open(output_file, "w") as f:
    for question, answer in questions_and_answers:
        entry = create_training_entry(question, answer)
        f.write(json.dumps(entry) + "\n")
