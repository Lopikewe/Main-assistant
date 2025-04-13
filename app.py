import os
from flask import Flask, request, jsonify
import openai
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Request Sharing (CORS)

# Add your OpenAI API key here
openai.api_key = "sk-proj-IcJoaXV0H4jxCBbDCtGqTZKnq-nrwjLktr1Q6nsb_Iy_rZxf-GshU84cDhF6YJeXQBXCPz2FcJT3BlbkFJ5adlhIXmjyHGjvxacB5lnX7jKvebKYBNAtdIXkWbvXKGTfkBREuzAin08gHokpwLN0aYZGF1"

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

        # Call OpenAI API for response
        response = openai.Completion.create(
            model="text-davinci-003",  # You can use your desired model
            prompt=message,
            max_tokens=150
        )

        answer = response.choices[0].text.strip()
        return jsonify({"response": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure app is binding to the correct port
    port = int(os.environ.get("PORT", 5000))  # Use the Render-provided port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)  # Listen on all interfaces
