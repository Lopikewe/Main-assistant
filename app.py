from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this line
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)
CORS(app)  # Add this line to allow CORS for all routes

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_message = data.get("message")

    # Create thread
    thread_res = requests.post("https://api.openai.com/v1/threads", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    })
    thread_id = thread_res.json()["id"]

    # Add user message to thread
    requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "role": "user",
        "content": user_message
    })

    # Run assistant
    run_res = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "assistant_id": ASSISTANT_ID
    })
    run_id = run_res.json()["id"]

    # Poll until run is complete
    while True:
        status_res = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}", headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        })
        status = status_res.json()
        if status["status"] == "completed":
            break
        time.sleep(1)

    # Get assistant response
    messages_res = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    })
    messages = messages_res.json()
    assistant_message = next(
        (msg for msg in messages["data"] if msg["role"] == "assistant"),
        {"content": [{"text": {"value": "No response"}}]}
    )

    answer = assistant_message["content"][0]["text"]["value"]
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

    return jsonify({"response": answer})

if __name__ == "__main__":
     app.run(debug=True, host="0.0.0.0", port=5000)
