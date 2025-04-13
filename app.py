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
@app.route("/",

