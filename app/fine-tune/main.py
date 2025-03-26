import os
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# Define the fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file="data/personal_responses.jsonl",
)