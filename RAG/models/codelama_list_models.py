import os
from groq import Groq

# Set API key
api_key = "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"  # Or use os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=api_key)

# List available models
models = client.models.list()

# Print the full response to see the structure
print(models)

# Iterate and print model details
for model in models:
    print(model)  # Debugging step to see what each model entry looks like
