import os
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Your assistant and thread IDs
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_ID = "thread_I1ypoK0YBZcwD4ZoXczpRaU1"  # Your thread ID

@app.route("/")
def home():
    return "📚 Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()  # Get the message sent in the POST request
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Step 1: Add message to thread
        openai.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=message
        )

        # Step 2: Run assistant
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
