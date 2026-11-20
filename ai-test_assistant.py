"""
Pytest suite for AquaNest AI Assistant
Validates role guardrails, data grounding, context memory, and safety rules.
"""

import pytest
import sys
import os

# Add paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from services.api_client import AquaNestApiClient
from assistant.assistant_service import AquaNestAssistant


@pytest.fixture
def assistant():
    client = AquaNestApiClient()
    return AquaNestAssistant(api_client=client)


def test_tank_query_grounding(assistant):
    text, fig = assistant.ask("What is the tank level?", user_role="ADMIN")
    assert "72.5%" in text or "tank level is" in text
    assert "L of water is available" in text


def test_pump_query_grounding(assistant):
    text, fig = assistant.ask("Is the pump ON?", user_role="ADMIN")
    assert "pump is currently" in text
    assert "Mode:" in text


def test_leakage_diagnostics(assistant):
    text, fig = assistant.ask("Are there any active leaks?", user_role="ADMIN")
    assert "leakage" in text.lower()
    assert "tank leakage" in text.lower() or "pipe leakage" in text.lower()


def test_demand_prediction_labeling(assistant):
    text, fig = assistant.ask("What is tomorrow's predicted demand?", user_role="ADMIN")
    assert "predicts approximately" in text
    assert "statistical predictions, not actual measurements" in text


def test_resident_access_own_flat(assistant):
    text, fig = assistant.ask("How much water did I consume today?", user_role="RESIDENT", user_house_id="H101")
    assert "House 101 consumed" in text
    assert "today" in text.lower()


def test_resident_cross_house_privacy_violation_denied(assistant):
    # Resident in Flat 101 attempts to peek at Flat 104
    text, fig = assistant.ask("How much water did House 104 use today?", user_role="RESIDENT", user_house_id="H101")
    assert text == "I can only provide information for your assigned house."


def test_admin_cross_house_allowed(assistant):
    text, fig = assistant.ask("How much water did House 104 consume today?", user_role="ADMIN")
    assert "House 104 consumed" in text


def test_conversational_context_retention(assistant):
    # Turn 1: Query House 102
    text1, _ = assistant.ask("How much did House 102 consume today?", user_role="ADMIN")
    assert "House 102 consumed" in text1

    # Turn 2: Contextual follow-up referring to "yesterday"
    text2, _ = assistant.ask("What about yesterday?", user_role="ADMIN")
    assert "House 102 consumed" in text2


def test_out_of_scope_query(assistant):
    text, fig = assistant.ask("What is the capital of France?", user_role="ADMIN")
    assert "I can help you with tank status, pump status, water consumption" in text
