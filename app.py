from flask import Flask, request, jsonify
import openai
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Set your OpenAI API Key
openai.api_key = "sk-proj-IcJoaXV0H4jxCBbDCtGqTZKnq-nrwjLktr1Q6nsb_Iy_rZxf-GshU84cDhF6YJeXQBXCPz2FcJT3BlbkFJ5adlhIXmjyHGjvxacB5lnX7jKvebKYBNAtdIXkWbvXKGTfkBREuzAin08gHokpwLN0aYZGF1"  # Replace with your actual API key

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Get the data from the incoming request
        data = request.get_json()
        user_message = data.get("message")
        
        # Log the incoming message for debugging
        logging.debug(f"Received message: {user_message}")

        if not user_message:
            logging.error("No message provided.")
            return jsonify({"error": "No message provided"}), 400

        # Make the request to OpenAI API
        response = openai.Completion.create(
            model="text-davinci-003",  # Use the model you'd like
            prompt=user_message,
            max_tokens=150
        )

        # Return the response from OpenAI
        logging.debug(f"OpenAI response: {response.choices[0].text.strip()}")
        return jsonify({"response": response.choices[0].text.strip()})

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
