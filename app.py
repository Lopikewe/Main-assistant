import os
import time
import logging
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- Load API key and assistant ID ---
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_FILE = "thread_id.txt"

if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# --- Load or create a shared thread ---
def load_or_create_thread():
    if os.path.exists(THREAD_FILE):
        with open(THREAD_FILE, "r") as f:
            thread_id = f.read().strip()
            logging.info(f"Loaded thread ID: {thread_id}")
            return thread_id
    thread = openai.beta.threads.create()
    with open(THREAD_FILE, "w") as f:
        f.write(thread.id)
    logging.info(f"Created new thread ID: {thread.id}")
    return thread.id

SHARED_THREAD_ID = load_or_create_thread()

# --- Generate response from assistant ---
def generate_response(message_body: str) -> str:
    openai.beta.threads.messages.create(
        thread_id=SHARED_THREAD_ID,
        role="user",
        content=message_body
    )

    run = openai.beta.threads.runs.create(
        thread_id=SHARED_THREAD_ID,
        assistant_id=ASSISTANT_ID
    )

    # Wait for run to complete
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=SHARED_THREAD_ID,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            raise Exception(f"Run failed with status: {run_status.status}")
        time.sleep(1)

    # Fetch latest assistant message
    messages = openai.beta.threads.messages.list(thread_id=SHARED_THREAD_ID)
    return messages.data[0].content[0].text.value

# --- Routes ---
@app.route("/")
def home():
    return "✅ Factory Assistant API is live."

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Missing 'message' field"}), 400

        logging.info(f"User asked: {message}")
        answer = generate_response(message)
        return jsonify({"response": answer})

    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_thread():
    try:
        thread = openai.beta.threads.create()
        thread_id = thread.id
        with open(THREAD_FILE, "w") as f:
            f.write(thread_id)
        global SHARED_THREAD_ID
        SHARED_THREAD_ID = thread_id
        logging.info(f"Thread reset to: {thread_id}")
        return jsonify({"message": "Thread reset successfully", "thread_id": thread_id})
    except Exception as e:
        logging.error(f"Error resetting thread: {e}")
        return jsonify({"error": str(e)}), 500

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
