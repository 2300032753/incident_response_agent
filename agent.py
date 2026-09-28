import os
from dotenv import load_dotenv
from google import genai

from hindsight_memory import recall_similar_incidents

load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    return genai.Client(api_key=api_key)


def generate_response(prompt):
    """
    Generate an AI response using Gemini.
    Automatically tries fallback models if one is unavailable.
    """

    client = get_gemini_client()

    models = [
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite"
    ]

    last_error = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.text:
                return response.text

        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(
        f"All Gemini models are currently unavailable. "
        f"Last error: {last_error}"
    )


def investigate_incident(incident):
    """
    Investigate the current incident using
    Hindsight's previous organizational memories.
    """

    query = f"""
We are investigating a production incident.

Title:
{incident['title']}

Service:
{incident['service']}

Severity:
{incident['severity']}

Error:
{incident['error']}

Description:
{incident['description']}

Find previous incidents with similar:
- symptoms
- errors
- services
- root causes
- resolutions
"""

    memories = recall_similar_incidents(query)

    if memories:
        memory_text = "\n\n".join(
            [
                f"Previous Memory {i + 1}:\n{m['text']}"
                for i, m in enumerate(memories)
            ]
        )
    else:
        memory_text = "No previous incidents were found."

    prompt = f"""
You are an AI Incident Response Engineer.

Investigate the current production incident.

CURRENT INCIDENT
----------------
Title: {incident['title']}
Service: {incident['service']}
Severity: {incident['severity']}

Error:
{incident['error']}

Description:
{incident['description']}

ORGANIZATIONAL MEMORY FROM HINDSIGHT
------------------------------------
{memory_text}

Provide the investigation using exactly these sections:

ROOT CAUSE
Give the most likely root cause.

HISTORICAL EVIDENCE
Explain whether previous incidents support this diagnosis.

PREVIOUS FIX
Describe any successful fix from previous incidents.

SUGGESTED RESOLUTION
Give practical steps to resolve the current incident.

LESSON
Give one concise lesson that should be remembered for future incidents.

Important:
- Use the Hindsight memories as historical evidence.
- Do not invent previous incidents.
- If no relevant memory exists, clearly say that this is a new pattern.
"""

    analysis = generate_response(prompt)

    return {
        "analysis": analysis,
        "memories": memories
    }


def ask_agent(question):
    """
    Answer a user question using Hindsight memory.
    """

    memories = recall_similar_incidents(question)

    if memories:
        memory_text = "\n\n".join(
            [
                m["text"]
                for m in memories
            ]
        )
    else:
        memory_text = "No relevant historical memory was found."

    prompt = f"""
You are an AI Incident Response Agent.

Answer the user's question using the organization's
historical incident memory.

USER QUESTION:
{question}

HISTORICAL MEMORY:
{memory_text}

Rules:

1. Use historical evidence when available.
2. Do not invent previous incidents.
3. If there is no relevant memory, say so.
4. Explain the answer clearly.
5. Mention incident IDs when available.
6. If a previous resolution is available, explain it.
"""

    return generate_response(prompt)