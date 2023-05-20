from flask import Flask, jsonify, request, abort
from dateutil.parser import parse
import os
import requests
import datetime
from dotenv import load_dotenv

app = Flask(__name__)

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

@app.route('/api/conflicting_appointments/<record_id>', methods=['GET'])
def get_conflicting_appointments(record_id: str):
    # same code here

# WSGI expects an object named 'app'
app = app.wsgi_app
