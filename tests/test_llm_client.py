from app.services.llm_client import call_llm


def test_mock_llm_response():
    response = call_llm("Hello Gateway")

    assert "LLM received" in response
    assert "Hello Gateway" in response