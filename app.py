from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Your OpenAI API key (replace this with your actual API key)
openai.api_key = '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'

@app.route('/')
def home():
    return 'Flask app is running'

@app.route('/ask', methods=["POST"])
def ask():
    try:
        # Extract the message from the incoming JSON request
        user_message = request.json.get('message')
        
        # Check if the message is provided
        if not user_message:
            return jsonify({"error": "Message not provided"}), 400

        # Request OpenAI API to generate an answer
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use the desired model
            prompt=user_message,
            max_tokens=150
        )

        # Extract the answer from the response
        answer = response.choices[0].text.strip()

        return jsonify({"response": answer})

    except Exception as e:
        # Log the full error message to the console
        print(f"Error occurred: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == '__main__':
    app.run(debug=True)

