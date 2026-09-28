import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_API_URL = os.getenv(
    "HINDSIGHT_API_URL",
    "https://api.hindsight.vectorize.io"
)

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "incident-response-agent"
)


def get_client():
    """Create Hindsight client."""
    if not HINDSIGHT_API_KEY:
        raise ValueError(
            "HINDSIGHT_API_KEY is missing. Add it to your .env file."
        )

    return Hindsight(
        base_url=HINDSIGHT_API_URL,
        api_key=HINDSIGHT_API_KEY
    )


def store_incident(incident):
    """Store an incident experience in Hindsight."""

    client = get_client()

    memory_text = f"""
Incident ID: {incident['id']}

Title: {incident['title']}

Service: {incident['service']}

Severity: {incident['severity']}

Error:
{incident['error']}

Description:
{incident['description']}

Root Cause:
{incident['root_cause']}

Resolution:
{incident['resolution']}

Lesson Learned:
{incident['lesson']}

Status:
{incident['status']}

Date:
{incident['date']}
"""

    client.retain(
        bank_id=BANK_ID,
        content=memory_text,
        context="Production incident investigation and resolution",
        metadata={
            "incident_id": incident["id"],
            "service": incident["service"],
            "severity": incident["severity"]
        }
    )

    return True


def recall_similar_incidents(query):
    """Search Hindsight for previous incidents."""

    client = get_client()

    result = client.recall(
        bank_id=BANK_ID,
        query=query,
        types=["experience", "observation"],
        max_tokens=3000,
        budget="mid"
    )

    memories = []

    for memory in result.results:
        memories.append({
            "type": memory.type,
            "text": memory.text,
            "context": memory.context
        })

    return memories


def reflect_on_incidents(query):
    """Use Hindsight to generate an answer from organizational memory."""

    client = get_client()

    response = client.reflect(
        bank_id=BANK_ID,
        query=query
    )

    return response.text


def get_all_memories():
    """Retrieve incident memories from Hindsight."""

    client = get_client()

    result = client.recall(
        bank_id=BANK_ID,
        query="previous production incidents, root causes, resolutions and lessons learned",
        max_tokens=5000,
        budget="mid"
    )

    memories = []

    for memory in result.results:
        memories.append({
            "type": memory.type,
            "text": memory.text,
            "context": memory.context
        })

    return memories