from flask import Flask, jsonify, request, abort
from dateutil.parser import parse
import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID = os.environ["AIRTABLE_BASE_ID"]
TABLE_NAME = os.environ["AIRTABLE_TABLE_NAME"]
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

@app.route("/api/conflicting_appointments/<record_id>", methods=['GET'])
def get_conflicting_appointments(record_id: str):
    response = requests.get(AIRTABLE_API_URL, headers=headers)
    appointments = response.json().get("records", [])

    appointment_to_check = None
    other_appointments = []

    today = datetime.datetime.now().date()

    for appointment in appointments:
        Start = datetime.datetime.fromisoformat(appointment["fields"]["Start"][:-1] + "+00:00")
        End = datetime.datetime.fromisoformat(appointment["fields"]["End"][:-1] + "+00:00")

        if Start.date() < today:
            continue

        if appointment["id"] == record_id:
            appointment_to_check = {"id": appointment["id"], "Start": Start, "end": End, "name": appointment["fields"]["Name"]}
        else:
            other_appointments.append({"id": appointment["id"], "Start": Start, "End": End, "name": appointment["fields"]["Name"]})

    if not appointment_to_check:
        return jsonify(is_conflict=False, conflicting_appointments=[], error="Record not found or has a Start date in the past")

    conflicting_appointments = []

    for appointment in other_appointments:
        if (appointment_to_check["Start"] <= appointment["Start"] < appointment_to_check["End"]) or (appointment_to_check["Start"] < appointment["End"] <= appointment_to_check["End"]) or (appointment["Start"] <= appointment_to_check["Start"] and appointment["End"] >= appointment_to_check["End"]):
            conflicting_appointments.append({"Appointment1": appointment_to_check["name"], "Appointment2": appointment["name"]})

    has_conflict = len(conflicting_appointments) > 0

    return jsonify(is_conflict=has_conflict, conflicting_appointments=conflicting_appointments, error=None)

if __name__ == "__main__":
    app.run(debug=True)
