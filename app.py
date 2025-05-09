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

# --- Get file URL by ID (for images) ---
def get_file_url(file_id):
    try:
        file_info = openai.files.retrieve(file_id)
        return f"https://api.openai.com/v1/files/{file_id}/content"
    except Exception as e:
        logging.error(f"Error fetching file URL: {e}")
        return None

# --- Default route ---
@app.route("/")
def home():
    return "✅ Factory Assistant API is live."

# --- Standard assistant response (non-stream) ---
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")
        if not message:
            return jsonify({"error": "Missing 'message' field"}), 400

        logging.info(f"User asked: {message}")

        openai.beta.threads.messages.create(
            thread_id=SHARED_THREAD_ID,
            role="user",
            content=message
        )

        run = openai.beta.threads.runs.create(
            thread_id=SHARED_THREAD_ID,
            assistant_id=ASSISTANT_ID
        )

        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=SHARED_THREAD_ID,
                run_id=run.id
            )
            if status.status == "completed":
                break
            elif status.status in ["failed", "cancelled"]:
                raise Exception(f"Run failed with status: {status.status}")
            time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=SHARED_THREAD_ID)
        return jsonify({"response": messages.data[0].content[0].text.value})

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Streaming assistant response ---
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
            fallback_used = True
            collected_text = ""
            start_time = time.time()

            stream = openai.beta.threads.runs.create(
                thread_id=SHARED_THREAD_ID,
                assistant_id=ASSISTANT_ID,
                stream=True
            )

            for event in stream:
                if hasattr(event, "delta") and event.delta:
                    parts = event.delta.get("content", [])
                    for part in parts:
                        text = ""
                        if isinstance(part, dict) and part.get("type") == "text":
                            text = part["text"]["value"]
                        elif hasattr(part, "type") and part.type == "text":
                            text = part.text.value
                        if text:
                            collected_text += text
                            fallback_used = False
                            yield f"data: {json.dumps({'text': text})}\n\n"

                if time.time() - start_time > 15 and fallback_used:
                    logging.warning("⚠️ No streaming chunks received — using fallback.")
                    break

            if fallback_used or not collected_text:
                messages = openai.beta.threads.messages.list(thread_id=SHARED_THREAD_ID)
                if messages.data:
                    last_msg = messages.data[0]
                    for chunk in last_msg.content:
                        if chunk.type == "text":
                            yield f"data: {json.dumps({'text': chunk.text.value})}\n\n"
                        elif chunk.type == "image_file":
                            file_url = get_file_url(chunk.image_file.file_id)
                            if file_url:
                                yield f"data: {json.dumps({'image_url': file_url})}\n\n"

        return Response(generate(), content_type='text/event-stream')

    except Exception as e:
        logging.error(f"Streaming error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Text-to-speech using OpenAI TTS ---
@app.route("/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        text = data.get("text")
        if not text:
            return jsonify({"error": "Missing 'text' field"}), 400

        response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",  # or shimmer, echo
            input=text
        )

        audio_bytes = response.read()
        return Response(audio_bytes, mimetype="audio/mpeg")

    except Exception as e:
        logging.error(f"TTS error: {e}")
        return jsonify({"error": str(e)}), 500

# --- Reset thread for testing ---
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
