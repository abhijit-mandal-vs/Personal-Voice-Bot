"""Tests for the response handling module."""

import pytest
import sys
import os

# Add the project root directory to the Python path FIRST
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# THEN import from the app module
from app.core.responses import get_response_context, PERSONAL_INFO, QUESTION_MAPPINGS


def test_get_response_context_life_story():
    """Test getting response context for life story questions."""
    question = "What should we know about your life story in a few sentences?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["life_story"]

    # Test with a variation
    question = "Tell me about yourself"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["life_story"]


def test_get_response_context_superpower():
    """Test getting response context for superpower questions."""
    question = "What's your #1 superpower?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["superpower"]

    # Test with a variation
    question = "What are you best at?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["superpower"]


def test_get_response_context_growth():
    """Test getting response context for growth area questions."""
    question = "What are the top 3 areas you'd like to grow in?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["growth_areas"]

    # Test with a variation
    question = "What are your weaknesses?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["growth_areas"]


def test_get_response_context_misconceptions():
    """Test getting response context for misconception questions."""
    question = "What misconception do your coworkers have about you?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["misconceptions"]

    # Test with a variation
    question = "How are you misunderstood?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["misconceptions"]


def test_get_response_context_boundaries():
    """Test getting response context for boundary questions."""
    question = "How do you push your boundaries and limits?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["boundaries"]

    # Test with a variation
    question = "How do you challenge yourself?"
    context = get_response_context(question)
    assert context == PERSONAL_INFO["boundaries"]


def test_get_response_context_unknown():
    """Test getting response context for unknown questions."""
    question = "What's your favorite color?"
    context = get_response_context(question)
    # Should return the default general context
    assert "thoughtful, introspective tone" in context.lower()
    assert context != PERSONAL_INFO["life_story"]
    assert context != PERSONAL_INFO["superpower"]
    assert context != PERSONAL_INFO["growth_areas"]
    assert context != PERSONAL_INFO["misconceptions"]
    assert context != PERSONAL_INFO["boundaries"]


def test_question_mappings_coverage():
    """Test that all keys in QUESTION_MAPPINGS map to valid keys in PERSONAL_INFO."""
    for keyword, info_key in QUESTION_MAPPINGS.items():
        assert (
            info_key in PERSONAL_INFO
        ), f"Key '{info_key}' from QUESTION_MAPPINGS not found in PERSONAL_INFO"
