import os
import logging
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Ensure the OpenAI API key is retrieved from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is missing and raise an error if it is
if openai.api_key is None:
    raise ValueError("API key is missing. Set the OPENAI_API_KEY environment variable.")

@app.route("/")
def home():
    return "Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")
        assistant_id = data.get("assistant_id")  # Get the assistant ID from the request data

        if not message:
            return jsonify({"error": "No message provided"}), 400

        if not assistant_id:
            return jsonify({"error": "Assistant ID is missing"}), 400  # Handle missing assistant ID

        # Call OpenAI API for response using the chat-based completion method
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use your specific model
            messages=[{"role": "user", "content": message}],
            max_tokens=150,
            user=assistant_id  # Pass the assistant ID as user context
        )

        # Get the response from the API
        answer = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": answer})

    except Exception as e:
        logging.error(f"Error during OpenAI API call: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure app is binding to the correct port
    port = int(os.environ.get("PORT", 5000))  # Use the Render-provided port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
