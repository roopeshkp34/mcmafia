import unittest
from pydantic import ValidationError
from app.models.chat import ChatResponse, AgentStep

class TestValidationFix(unittest.TestCase):
    def test_chat_response_validation(self):
        # Case 1: Step with content only (no tool_calls)
        content_step = {
            "agent": "rag_agent",
            "content": "I couldn't find specific information about Apple's profit..."
        }
        
        # Case 2: Step with tool fields but no tool_calls
        tool_step = {
            "agent": "supervisor",
            "tool": "transfer_to_rag_agent",
            "input": {}
        }
        
        # Case 3: Step with tool_calls
        tool_calls_step = {
            "agent": "supervisor",
            "tool_calls": [{"name": "some_tool", "args": {}}]
        }
        
        # Case 4: Agent name is "supervisor" (default)
        supervisor_step = {
            "agent": "supervisor",
            "content": "Starting process"
        }

        data = {
            "response": "Apple made $97B profit.",
            "agent_steps": [content_step, tool_step, tool_calls_step, supervisor_step],
            "reasoning_for_response": "Logic execution completed successfully."
        }
        
        try:
            response = ChatResponse(**data)
            self.assertEqual(len(response.agent_steps), 4)
            print("Validation successful!")
        except Exception as e:
            self.fail(f"Validation failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
