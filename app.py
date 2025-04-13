import os
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = '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'

@app.route('/')
def home():
    return 'Flask app is running'

@app.route('/ask', methods=["POST"])
def ask():
    try:
        # Extract the user's message from the incoming JSON request
        user_message = request.json.get('message')

        # Check if the message is provided
        if not user_message:
            return jsonify({"error": "Message not provided"}), 400

        # Request OpenAI API to generate a response
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the desired model
            prompt=user_message,
            max_tokens=150
        )

        # Extract the answer from the response
        answer = response.choices[0].text.strip()

        # Return the response back to the client
        return jsonify({"response": answer})

    except Exception as e:
        # Log the error message in the console
        print(f"Error occurred: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)  # Use the environment variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)

