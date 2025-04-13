from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"}), 200

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Create thread
    thread = requests.post("https://api.openai.com/v1/threads", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }).json()
    thread_id = thread["id"]

    # Add message
    requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={"role": "user", "content": user_message})

    # Run assistant
    run = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={"assistant_id": ASSISTANT_ID}).json()

    run_id = run["id"]

    # Wait for response
    while True:
        run_check = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }).json()
        if run_check["status"] == "completed":
            break
        time.sleep(1)

    # Get assistant response
    messages = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }).json()

    for msg in messages["data"]:
        if msg["role"] == "assistant":
            return jsonify({"response": msg["content"][0]["text"]["value"]})

    return jsonify({"response": "No assistant reply found."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
