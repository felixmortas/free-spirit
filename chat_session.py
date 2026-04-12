import uuid
from langchain.messages import HumanMessage, AIMessage


class ChatSession:
    """Manages the conversation history in memory via the agent's checkpointer."""

    def __init__(self, agent, langfuse_handler=None):
        self.agent = agent
        self.langfuse_handler = langfuse_handler
        # A unique thread ID is generated at startup
        self.thread_id = str(uuid.uuid4())

    def _get_config(self) -> dict:
        """Returns the configuration required for the agent."""
        config = {"configurable": {"thread_id": self.thread_id}}
        if self.langfuse_handler:
            config["callbacks"] = [self.langfuse_handler]
            config["metadata"] = {"langfuse_tags": ["Free-Spirit"]}
        return config

    def send(self, user_input: str) -> str:
        """Send only the new message to the agent."""
        user_msg = HumanMessage(content=user_input)

        # Only the latest message is sent. 
        # LangGraph handles the history using the thread_id.
        result = self.agent.invoke(
            {"messages": [user_msg]},
            config=self._get_config(),
        )

        return self._extract_ai_message(result)

    def reset(self):
        """Clears the history by generating a new thread_id."""
        # By changing the ID, LangGraph treats the rest of the conversation as a new one
        self.thread_id = str(uuid.uuid4())

    def get_history(self) -> list[dict]:
        """Retrieves the history directly from the agent's internal state."""
        output = []
        
        # We retrieve the current status associated with our thread_id
        state = self.agent.get_state(self._get_config())
        
        # 'messages' contains the complete list synchronized by LangGraph
        messages = state.values.get("messages", [])

        for msg in messages:
            if isinstance(msg, HumanMessage):
                output.append({"role": "Vous", "content": msg.content})
            elif isinstance(msg, AIMessage):
                output.append({"role": "Agent", "content": msg.content})
                
        return output

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_ai_message(self, result) -> str:
        if isinstance(result, dict):
            if "messages" in result:
                last = result["messages"][-1]
                return last.content if hasattr(last, "content") else str(last)
            if "output" in result:
                return result["output"]
        return str(result)