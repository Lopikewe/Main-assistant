import os
import time
import logging
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Configuration ---
ASSISTANT_ID = "asst_zaP9DAqsurHvabQuvRKh7VtX"
THREAD_FILE = "thread_id.txt"

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- Load OpenAI API key ---
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# --- Thread ID Management ---
def
