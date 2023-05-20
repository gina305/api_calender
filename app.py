from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dateutil.parser import parse
import os
import requests
import datetime
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_KEY = os.environ["AIRTABLE_API_KEY"]
BASE_ID = os.environ["AIRTABLE_BASE_ID"]
TABLE_NAME = os.environ["AIRTABLE_TABLE_NAME"]
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

class ConflictResult(BaseModel):
    is_conflict: bool
    conflicting_appointments: list
    error: Optional[str] = None

@app.get("/api/conflicting_appointments/{record_id}", response_model=ConflictResult)
async def get_conflicting_appointments(record_id: str):
    try:
        response = requests.get(AIRTABLE_API_URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    appointments = response.json().get("records", [])

    print(appointments)
    appointment_to_check = None
    other_appointments = []

    today = datetime.datetime.now().date()

    for appointment in appointments:
        try:
            Start = datetime.datetime.fromisoformat(appointment["fields"]["Start"][:-1] + "+00:00")
            End = datetime.datetime.fromisoformat(appointment["fields"]["End"][:-1] + "+00:00")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing date: {str(e)}")

        if Start.date() < today:
            continue

        if appointment["id"] == record_id:
            appointment_to_check = {"id": appointment["id"], "Start": Start, "end": End, "name": appointment["fields"]["Name"]}
        else:
            other_appointments.append({"id": appointment["id"], "Start": Start, "End": End, "name": appointment["fields"]["Name"]})

    if not appointment_to_check:
        return {"is_conflict": False, "conflicting_appointments": [], "error": "Record not found or has a Start date in the past"}

    conflicting_appointments = []

    for appointment in other_appointments:
        if (appointment_to_check["Start"] <= appointment["Start"] < appointment_to_check["End"]) or (appointment_to_check["Start"] < appointment["End"] <= appointment_to_check["End"]) or (appointment["Start"] <= appointment_to_check["Start"] and appointment["End"] >= appointment_to_check["End"]):
            conflicting_appointments.append({"Appointment1": appointment_to_check["name"], "Appointment2": appointment["name"]})

    has_conflict = len(conflicting_appointments) > 0

    return {"is_conflict": has_conflict, "conflicting_appointments": conflicting_appointments}
