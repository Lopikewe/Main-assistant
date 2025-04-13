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

# Assistant ID (use your actual ID here)
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"

@app.route("/")
def home():
    return "Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        message = data.get("message")

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Call OpenAI API for response using the gpt-4o-mini model and passing the assistant ID
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Change the model to gpt-4o-mini
            messages=[{"role": "user", "content": message}],
            max_tokens=150,
            user=ASSISTANT_ID  # Add the assistant ID here to make sure the right assistant is used
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
