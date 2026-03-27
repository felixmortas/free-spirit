import uuid
from langchain.messages import HumanMessage, AIMessage


class ChatSession:
    """Gère l'historique de conversation en mémoire via le checkpointer de l'agent."""

    def __init__(self, agent, langfuse_handler=None):
        self.agent = agent
        self.langfuse_handler = langfuse_handler
        # On génère un ID de thread unique au démarrage
        self.thread_id = str(uuid.uuid4())

    def _get_config(self) -> dict:
        """Retourne la configuration nécessaire pour l'agent."""
        config = {"configurable": {"thread_id": self.thread_id}}
        if self.langfuse_handler:
            config["callbacks"] = [self.langfuse_handler]
        return config

    def send(self, user_input: str) -> str:
        """Envoie uniquement le nouveau message à l'agent."""
        user_msg = HumanMessage(content=user_input)

        # On envoie UNIQUEMENT le dernier message. 
        # LangGraph s'occupe de l'historique grâce au thread_id.
        result = self.agent.invoke(
            {"messages": [user_msg]},
            config=self._get_config(),
        )

        return self._extract_ai_message(result)

    def reset(self):
        """Efface l'historique en générant un nouveau thread_id."""
        # En changeant l'ID, LangGraph traite la suite comme une nouvelle conversation
        self.thread_id = str(uuid.uuid4())

    def get_history(self) -> list[dict]:
        """Récupère l'historique directement depuis l'état interne de l'agent."""
        output = []
        
        # On extrait l'état actuel lié à notre thread_id
        state = self.agent.get_state(self._get_config())
        
        # 'messages' contient la liste complète synchronisée par LangGraph
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