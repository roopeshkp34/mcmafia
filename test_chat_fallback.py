import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from typing import List, Dict, Any, Optional, Union

# Mock the dependencies before importing chat_service
import sys
from pydantic import BaseModel, Field

sys.modules["langchain_openai"] = MagicMock()
sys.modules["langgraph.prebuilt"] = MagicMock()
sys.modules["langgraph_supervisor"] = MagicMock()
sys.modules["app.core.config"] = MagicMock()
sys.modules["app.db.elasticsearch_client"] = MagicMock()
sys.modules["app.services.embedding"] = MagicMock()

# Now we can import the classes from chat.py
from app.services.chat import ChatService, SupervisorResponse, SourceDocumentInfo

async def test_source_mapping():
    print("Testing source mapping and fallback extraction...")
    
    chat_service = ChatService()
    
    # Mock result from ainvoke
    mock_json_content = {
        "reasoning_for_response": "I analyzed the data.",
        "response": "The answer.",
        "sources": [
            {
                "page_no": 10,
                "original_text": ["Raw text from document"],
                "file_name": "report.pdf",
                "bounding_box": [10.0, 20.0, 30.0, 40.0]
            }
        ]
    }
    
    class MockMessage:
        def __init__(self, content, name, msg_type="ai"):
            self.content = content
            self.name = name
            self.type = msg_type
            self.tool_calls = []
        
        def __getattr__(self, name):
            return None

    tool_output = [{
        "page_no": 10,
        "file_name": "report.pdf",
        "bounding_box": [[10.0, 20.0, 30.0, 40.0]],
        "original_text": ["Raw text from document"]
    }]

    messages = [
        MockMessage(json.dumps(tool_output), "rag_agent", "tool"),
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
    print(f"Sources: {result['source_documents']}")
    
    assert result["response"] == mock_json_content["response"]
    assert len(result["source_documents"]) == 1
    src = result["source_documents"][0]
    assert src["page_no"] == 10
    assert src["file_name"] == "report.pdf"
    assert src["original_text"] == "Raw text from document"
    assert src["bounding_box"] == [[10.0, 20.0, 30.0, 40.0]]
    
    print("Test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_source_mapping())
