from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all origins (you can modify this to be more restrictive if needed)
CORS(app, resources={r"/*": {"origins": "*"}})

# Get OpenAI API key and Assistant ID from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"

# Home route to handle GET and OPTIONS
@app.route("/", methods=["GET", "OPTIONS"])
def home():
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        return jsonify({"message": "CORS preflight successful"}), 200
    return jsonify({"message": "Welcome to the AI assistant"}), 200

# /ask route to handle POST and OPTIONS requests
@app.route("/ask", methods=["POST", "OPTIONS"])
def ask():
    if request.method == "OPTIONS":
        # Handle CORS preflight request for /ask endpoint
        return jsonify({"message": "CORS preflight successful"}), 200

    # Normal POST request handling
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Create a thread
    thread_res = requests.post("https://api.openai.com/v1/threads", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    })
    
    if thread_res.status_code != 200:
        return jsonify({"error": "Failed to create thread"}), 500

    thread_id = thread_res.json()["id"]

    # Add user message to thread
    message_res = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "role": "user",
