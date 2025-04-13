import os
import logging
import time
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

# Logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("API key is missing. Set the OPENAI_API_KEY environment variable.")

# Set your assistant ID and persistent thread ID
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_ID = "thread_abcd1234xyz"  # Replace with your actual thread ID

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

        # Step 1: Add the user's message to the existing thread
        openai.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=message
        )

        # Step 2: Run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=THREAD_ID,
            assistant_id=ASSISTANT_ID
        )

        # Step 3: Wait for run to complete
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=THREAD_ID,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Step 4: Get assistant response
        messages = openai.beta.threads.messages.list(thread_id=THREAD_ID)
        assistant_response = messages.data[0].content[0].text.value

        return jsonify({"response": assistant_response})

    except Exception as e:
        logging.error(f"Error during Assistant API call: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
