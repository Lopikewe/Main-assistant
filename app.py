import os
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Your assistant and thread IDs
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_ID = "thread_I1ypoK0YBZcwD4ZoXczpRaU1"  # Your thread ID

@app.route("/")
def home():
    return "📚 Manufacturing Assistant API is live!"

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data
