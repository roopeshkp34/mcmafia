import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from typing import List, Dict, Any, Optional

# Mock the dependencies before importing chat_service
import sys
from pydantic import BaseModel, Field

# Create a dummy SupervisorResponse if needed or just use the one from chat
# But we need to mock AzureChatOpenAI and other things

# Mocking the imports in app.services.chat
class MockLLM:
    pass

sys.modules["langchain_openai"] = MagicMock()
sys.modules["langgraph.prebuilt"] = MagicMock()
sys.modules["langgraph_supervisor"] = MagicMock()
sys.modules["app.core.config"] = MagicMock()
sys.modules["app.db.elasticsearch_client"] = MagicMock()
sys.modules["app.services.embedding"] = MagicMock()

# Now we can import the classes from chat.py
from app.services.chat import ChatService, SupervisorResponse, SourceDocumentInfo

async def test_fallback_parsing():
    print("Testing JSON parsing fallback...")
    
    chat_service = ChatService()
    
    # Mock result from ainvoke
    mock_json_content = {
        "reasoning_for_response": "I analyzed the data and found a trend.",
        "response": "The revenue increased by 10%.",
        "sources": [
            {
                "page_no": 10,
                "original_text": "Revenue grew from 100 to 110",
                "file_name": "report.pdf",
                "bounding_box": [10.0, 20.0, 30.0, 40.0]
            }
        ]
    }
    
    class MockMessage:
        def __init__(self, content, name):
            self.content = content
            self.name = name
            self.type = "ai"
            self.tool_calls = []
        
        def __getattr__(self, name):
            return None

    messages = [
        MockMessage("Some previous message", "data_extraction_agent"),
        MockMessage(json.dumps(mock_json_content), "supervisor")
    ]
    
    mock_result = {
        "messages": messages,
        "structured_response": None # Simulate failure to parse structured response
    }
    
    chat_service.app.ainvoke = AsyncMock(return_value=mock_result)
    
    # Run the chat method
    result = await chat_service.chat("test query")
    
    # Verify results
    print(f"Response: {result['response']}")
    print(f"Reasoning: {result['reasoning_for_response']}")
    print(f"Sources: {result['source_documents']}")
    
    assert result["response"] == mock_json_content["response"]
    assert result["reasoning_for_response"] == mock_json_content["reasoning_for_response"]
    assert len(result["source_documents"]) == 1
    assert result["source_documents"][0]["page_no"] == 10
    assert result["source_documents"][0]["file_name"] == "report.pdf"
    assert result["source_documents"][0]["bounding_box"] == [mock_json_content["sources"][0]["bounding_box"]]
    
    print("Test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_fallback_parsing())
