import os
import logging
import time
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("API key is missing. Set the OPENAI_API_KEY environment variable.")

# Use your specific Assistant ID
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"

@app.route("/")
def home():
    return "Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Step 1: Create a new thread
        thread = openai.beta.threads.create()

        # Step 2: Add the user message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )

        # Step 3: Run the assistant on that thread
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Step 4: Wait for the run to complete
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Step 5: Get the assistant's response
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        assistant_response = messages.data[0].content[0].text.value

        return jsonify({"response": assistant_response})

    except Exception as e:
        logging.error(f"Error during Assistant API call: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os
