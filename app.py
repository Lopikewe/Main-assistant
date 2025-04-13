import os
import logging
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Ensure no proxies are set
openai.proxy = None  # Clear any proxy settings if they're mistakenly being used

@app.route("/")
def home():
    return "📚 Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Send message to OpenAI API
        response = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": message}],
            thread="thread_I1ypoK0YBZcwD4ZoXczpRaU1"  # Pass the thread ID
        )

        # Get the assistant's response
        assistant_response = response['choices'][0]['message']['content'].strip()

        return jsonify({"response": assistant_response})

    except Exception as e:
        logging.error(f"Error during Assistant API call: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
