from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure this is set in Render

assistant_id = "asst_zaP9DAqsurHvabQuvRKh7VtX"  # your actual Assistant ID

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        client = openai.OpenAI()

        # Create a new thread
        thread = client.beta.threads.create()
        thread_id = thread.id  # ✅ Fixed here

        # Add the user message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        # Poll until it's done
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            if run_status.status == "completed":
                break

        # Retrieve the assistant's reply
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        answer = messages.data[0].content[0].text.value

        return jsonify({"response": answer})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return "<h1>Assistant is running</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

