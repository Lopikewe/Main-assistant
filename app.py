import os
import time
import logging
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

# Logging setup
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Load OpenAI credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
if not ASSISTANT_ID:
    raise ValueError("Missing OPENAI_ASSISTANT_ID environment variable")

# Create a shared thread at app startup
shared_thread = openai.beta.threads.create()
SHARED_THREAD_ID = shared_thread.id
logging.info(f"Using shared thread ID: {SHARED_THREAD_ID}")

@app.route("/")
def home():
    return "Manufacturing Assistant API (shared thread) is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Missing 'message' field"}), 400

        # Step 1: Add message to shared thread
        openai.beta.threads.messages.create(
            thread_id=SHARED_THREAD_ID,
            role="user",
            content=message
        )

        # Step 2: Run assistant
        run = openai.beta.threads.runs.create(
            thread_id=SHARED_THREAD_ID,
            assistant_id=ASSISTANT_ID
        )

        # Step 3: Wait for run completion
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=SHARED_THREAD_ID,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run {run_status.status}")
            time.sleep(1)

        # Step 4: Get latest assistant message
        messages = openai.beta.threads.messages.list(thread_id=SHARED_THREAD_ID)
        latest = messages.data[0].content[0].text.value

        return jsonify({"response": latest})

    except Exception as e:
        logging.error(f"OpenAI Assistant API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
