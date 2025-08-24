import pytest
from pydantic import ValidationError
from lexilearn.models.grammar import LanggraphGrammarNodeOutput

def test_langgraph_grammar_node_output_valid():
    """Tests successful creation of LanggraphGrammarNodeOutput with valid data."""
    data = {
        "processed_text": "Das ist ein Test.",
        "analysis": {"mood": "indicative"}
    }
    node_output = LanggraphGrammarNodeOutput(**data)
    assert node_output.processed_text == data["processed_text"]
    assert node_output.analysis == data["analysis"]

def test_langgraph_grammar_node_output_minimal():
    """Tests successful creation with only required fields."""
    data = {
        "processed_text": "Nur Text."
    }
    node_output = LanggraphGrammarNodeOutput(**data)
    assert node_output.processed_text == data["processed_text"]
    assert node_output.analysis is None

def test_langgraph_grammar_node_output_missing_required_field():
    """Tests that ValidationError is raised if a required field (processed_text) is missing."""
    with pytest.raises(ValidationError):
        LanggraphGrammarNodeOutput(analysis={"error": "missing text"})

def test_langgraph_grammar_node_output_invalid_type():
    """Tests that ValidationError is raised if a field has an invalid type."""
    with pytest.raises(ValidationError):
        LanggraphGrammarNodeOutput(processed_text=12345) # type: ignore

    with pytest.raises(ValidationError):
        LanggraphGrammarNodeOutput(processed_text="Valid text", analysis="not a dict") # type: ignore

# Example of how you might test with more complex, specific fields if added later:
# def test_langgraph_grammar_node_output_with_specific_fields():
#     data = {
#         "processed_text": "Der schnelle braune Fuchs.",
#         "analysis": {"tense": "present", "voice": "active"},
#         "sentence_type": "declarative",
#         "key_terms": ["Fuchs", "schnelle"]
#     }
#     # Assuming LanggraphGrammarNodeOutput is updated to include sentence_type and key_terms
#     # node_output = LanggraphGrammarNodeOutput(**data)
#     # assert node_output.sentence_type == data["sentence_type"]
#     # assert node_output.key_terms == data["key_terms"]
#     pass # Placeholder until model is updated 