import json
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from agent import investigate_incident, ask_agent
from hindsight_memory import (
    store_incident,
    get_all_memories
)


load_dotenv()


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Incident Response AI",
    page_icon="🚨",
    layout="wide"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .incident-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        background-color: #161b22;
        margin-bottom: 15px;
    }

    .memory-card {
        padding: 18px;
        border-radius: 12px;
        border-left: 4px solid #00c2ff;
        background-color: #161b22;
        margin-bottom: 12px;
    }

    .hero {
        padding: 25px;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            #111827,
            #172554
        );
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# LOAD INCIDENTS
# ---------------------------------------------------------

DATA_FILE = "data/incidents.json"


def load_incidents():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_incidents(incidents):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            incidents,
            f,
            indent=2
        )


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "incidents" not in st.session_state:
    st.session_state.incidents = load_incidents()

if "investigation" not in st.session_state:
    st.session_state.investigation = None


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🚨 Incident Response AI")

st.sidebar.caption(
    "AI-powered incident investigation with persistent memory"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🚨 Report Incident",
        "🔎 AI Investigation",
        "🧠 Memory",
        "💬 Agent Chat"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "📊 Dashboard":

    st.markdown(
        """
        <div class="hero">

        <h1>🚨 Incident Response AI</h1>

        <p>
        An AI incident-response agent that remembers
        previous incidents and learns from organizational experience.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    incidents = st.session_state.incidents

    active = len(
        [
            i for i in incidents
            if i["status"] != "Resolved"
        ]
    )

    previous = len(incidents)

    resolved = len(
        [
            i for i in incidents
            if i["status"] == "Resolved"
        ]
    )


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Active Incidents",
            active
        )

    with col2:
        st.metric(
            "Previous Incidents",
            previous
        )

    with col3:
        st.metric(
            "Resolved",
            resolved
        )


    st.divider()

    st.subheader("📋 Incident History")


    for incident in reversed(incidents):

        with st.container():

            st.markdown(
                f"""
                <div class="incident-card">

                <h3>
                {incident['id']} — {incident['title']}
                </h3>

                <b>Service:</b> {incident['service']}<br>

                <b>Severity:</b> {incident['severity']}<br>

                <b>Status:</b> {incident['status']}<br>

                <b>Date:</b> {incident['date']}

                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# REPORT INCIDENT
# =========================================================

elif page == "🚨 Report Incident":

    st.title("🚨 Report New Incident")

    st.write(
        "Describe the incident and let the AI investigate it "
        "using organizational memory."
    )


    title = st.text_input(
        "Incident Title",
        placeholder="Database Connection Timeout"
    )


    error = st.text_area(
        "Error / Log",
        placeholder="ERROR: connection timeout after 30 seconds"
    )


    col1, col2 = st.columns(2)


    with col1:

        severity = st.selectbox(
            "Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )


    with col2:

        service = st.text_input(
            "Service",
            placeholder="Order Service"
        )


    description = st.text_area(
        "Description",
        placeholder="Describe what happened..."
    )


    if st.button(
        "🔎 Analyze Incident",
        type="primary",
        use_container_width=True
    ):

        if not title or not error or not service:

            st.error(
                "Please provide title, error and service."
            )

        else:

            incident_number = len(
                st.session_state.incidents
            ) + 1

            incident = {
                "id": f"INC-{incident_number:03d}",
                "title": title,
                "error": error,
                "severity": severity,
                "service": service,
                "description": description,
                "root_cause": "Under investigation",
                "resolution": "Under investigation",
                "lesson": "Pending investigation",
                "status": "Investigating",
                "date": datetime.now().strftime("%Y-%m-%d")
            }


            with st.spinner(
                "🧠 Searching organizational memory..."
            ):

                try:

                    result = investigate_incident(
                        incident
                    )

                    st.session_state.investigation = {
                        "incident": incident,
                        "result": result
                    }

                    st.success(
                        "Investigation completed!"
                    )

                    st.success(
    "Investigation completed! Open the 'AI Investigation' page from the sidebar."
)

                except Exception as e:

                    st.error(
                        f"Investigation failed: {e}"
                    )


# =========================================================
# AI INVESTIGATION
# =========================================================

elif page == "🔎 AI Investigation":

    st.title("🔎 AI Investigation")


    investigation = st.session_state.investigation


    if not investigation:

        st.info(
            "No new incident has been investigated yet."
        )

        st.write(
            "Go to **Report Incident** to investigate a new incident."
        )

    else:

        incident = investigation["incident"]

        result = investigation["result"]


        st.subheader(
            f"{incident['id']} — {incident['title']}"
        )


        st.write(
            f"**Service:** {incident['service']}"
        )

        st.write(
            f"**Severity:** {incident['severity']}"
        )


        st.divider()


        # -------------------------------------------------
        # HISTORICAL MEMORY
        # -------------------------------------------------

        st.subheader(
            "🧠 Historical Memory"
        )


        memories = result["memories"]


        if memories:

            st.success(
                f"Found {len(memories)} relevant historical memories."
            )


            for memory in memories:

                st.markdown(
                    f"""
                    <div class="memory-card">

                    <b>Memory Type:</b>
                    {memory['type']}

                    <br><br>

                    {memory['text']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.warning(
                "No similar historical incident was found."
            )


        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        st.subheader(
            "🤖 AI Investigation"
        )

        st.markdown(
            result["analysis"]
        )


        # -------------------------------------------------
        # SAVE RESOLUTION
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "💾 Record Resolution"
        )


        root_cause = st.text_area(
            "Confirmed Root Cause",
            value="Database connection pool exhaustion"
        )


        resolution = st.text_area(
            "Resolution",
            value="Increased database connection pool size from 20 to 50."
        )


        lesson = st.text_area(
            "Lesson Learned",
            value="Check database connection pool utilization when database timeouts occur during traffic spikes."
        )


        if st.button(
            "🧠 Save Incident to Hindsight",
            type="primary",
            use_container_width=True
        ):

            incident["root_cause"] = root_cause
            incident["resolution"] = resolution
            incident["lesson"] = lesson
            incident["status"] = "Resolved"


            try:

                store_incident(
                    incident
                )


                st.session_state.incidents.append(
                    incident
                )


                save_incidents(
                    st.session_state.incidents
                )


                st.success(
                    "🎯 Incident resolved and learned by Hindsight!"
                )


                st.balloons()


            except Exception as e:

                st.error(
                    f"Could not save memory: {e}"
                )


# =========================================================
# MEMORY
# =========================================================

elif page == "🧠 Memory":

    st.title("🧠 Organizational Memory")


    st.write(
        """
        This page shows what the Incident Response Agent
        has learned from previous incidents.
        """
    )


    if st.button(
        "🔄 Refresh Hindsight Memory"
    ):

        try:

            memories = get_all_memories()

            st.session_state.memories = memories

        except Exception as e:

            st.error(
                f"Could not retrieve memories: {e}"
            )


    if "memories" not in st.session_state:

        st.info(
            "Click **Refresh Hindsight Memory**."
        )

    else:

        memories = st.session_state.memories


        if not memories:

            st.warning(
                "No memories found."
            )

        else:

            for memory in memories:

                st.markdown(
                    f"""
                    <div class="memory-card">

                    <b>Type:</b> {memory['type']}<br>

                    <b>Context:</b> {memory['context']}<br><br>

                    {memory['text']}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =========================================================
# AGENT CHAT
# =========================================================

elif page == "💬 Agent Chat":

    st.title("💬 Ask the Incident Response Agent")


    st.write(
        "Ask questions about previous incidents and organizational learning."
    )


    question = st.text_area(
        "Your question",
        placeholder=(
            "Have we seen this problem before?"
        )
    )


    if st.button(
        "🤖 Ask Agent",
        type="primary"
    ):

        if not question:

            st.warning(
                "Please enter a question."
            )

        else:

            with st.spinner(
                "🧠 Recalling organizational memory..."
            ):

                try:

                    answer = ask_agent(
                        question
                    )

                    st.subheader(
                        "🤖 Agent Response"
                    )

                    st.markdown(
                        answer
                    )

                except Exception as e:

                    st.error(
                        f"Agent error: {e}"
                    )