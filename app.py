import os
import time
import logging
import json
import openai
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- OpenAI Configuration ---
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_FILE = "thread_id.txt"

if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# --- Persistent thread management ---
def load_or_create_thread():
    if os.path.exists(THREAD_FILE):
        with open(THREAD_FILE, "r") as f:
            thread_id = f.read().strip()
            logging.info(f"Loaded existing thread ID: {thread_id}")
            return thread_id
    thread = openai.beta.threads.create()
    with open(THREAD_FILE, "w") as f:
        f.write(thread.id)
    logging.info(f"Created new thread ID: {thread.id}")
    return thread.id

SHARED_THREAD_ID = load_or_create_thread()

# --- Non-streaming assistant response ---
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

@app.route("/stream-ask", methods=["POST"])
def stream_ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "Missing 'message' field"}), 400

        # Add user message to the thread
        openai.beta.threads.messages.create(
            thread_id=SHARED_THREAD_ID,
            role="user",
            content=message
        )

        def generate():
            fallback_used = True
            collected_text = ""

            # Start run with streaming
            stream = openai.beta.threads.runs.create(
                thread_id=SHARED_THREAD_ID,
                assistant_id=ASSISTANT_ID,
                stream=True
            )

            for event in stream:
                if hasattr(event, "delta") and event.delta:
                    parts = event.delta.get("content", [])
                    for part in parts:
                        if part.get("type") == "text":
                            text = part["text"]["value"]
                            collected_text += text
                            fallback_used = False
                            yield f"data: {json.dumps({'text': text})}\n\n"

            # If nothing was streamed, use fallback
            if fallback_used:
                logging.warning("⚠️ No streaming chunks received — using fallback.")
                time.sleep(1)
                messages = openai.beta.threads.messages.list(thread_id=SHARED_THREAD_ID)
                if messages.data:
                    last_message = messages.data[0]
                    chunks = last_message.content
                    for chunk in chunks:
                        if chunk.get("type") == "text":
                            text = chunk["text"]["value"]
                            yield f"data: {json.dumps({'text': text})}\n\n"

        return Response(generate(), content_type='text/event-stream')

    except Exception as e:
        logging.error(f"Streaming error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_thread():
    try:
        thread = openai.beta.threads.create()
        with open(THREAD_FILE, "w") as f:
            f.write(thread.id)
        global SHARED_THREAD_ID
        SHARED_THREAD_ID = thread.id
        logging.info(f"Thread reset to: {thread.id}")
        return jsonify({"message": "Thread reset successfully", "thread_id": thread.id})
    except Exception as e:
        logging.error(f"Error resetting thread: {e}")
        return jsonify({"error": str(e)}), 500

# --- Run the app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
