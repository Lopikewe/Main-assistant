import os
import time
import logging
import json
import openai
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- Config ---
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
SHARED_THREAD_ID = "thread_jpyWKedJMELyaODFUgzb6yqH"

if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# --- Generate full response (non-streaming) ---
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
    return "✅ Factory Assistant API (using fixed thread) is live."

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

        openai.beta.threads.messages.create(
            thread_id=SHARED_THREAD_ID,
            role="user",
            content=message
        )

        def generate():
            stream = openai.beta.threads.runs.create(
                thread_id=SHARED_THREAD_ID,
                assistant_id=ASSISTANT_ID,
                stream=True
            )

            for chunk in stream:
                try:
                    parts = chunk.data.get("step_details", {}).get("message_creation", {}).get("message", {}).get("content", [])
                    for part in parts:
                        if part.get("type") == "text":
                            text = part["text"]["value"]
                            yield f"data: {json.dumps({'text': text})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(generate(), content_type='text/event-stream')

    except Exception as e:
        logging.error(f"Streaming error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
