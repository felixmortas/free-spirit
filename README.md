# 🤖 ReAct Agent Chatbot

A robust, terminal-based conversational agent built with **LangChain** and **LangGraph**. This project implements a ReAct (Reasoning and Acting) loop, allowing the agent to use custom tools, maintain conversation memory via a persistent checkpointer, and track all operations through **Langfuse**.

## ✨ Features

-   **ReAct Logic**: The agent doesn't just chat; it reasons about which tools to use to solve complex queries.
-   **Short-term Memory**: Uses LangGraph `Checkpointers` to maintain context across a conversation thread.
-   **Observability**: Full integration with Langfuse to monitor latency, costs, and traces.
-   **Resilience**: Middleware support for model fallbacks if the primary LLM provider is down.
-   **Terminal Commands**: Built-in commands like `/reset` to clear history and `/history` to view the log.

## 🚀 Getting Started

### 1. Prerequisites
- [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your machine.
- API Keys for your LLM provider (e.g., Mistral, OpenAI, or Gemini) and Langfuse.

### 2. Installation
Clone the repository and create the environment:
```bash
conda env create -f environment.yml
conda activate free-spirit
```

### 3. Environment Setup
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST="https://cloud.langfuse.com"
ANYSCALE_API_KEY=your_key_here
# Add other provider keys as needed
```

### 4. Running the Chatbot
Launch the terminal interface:
```bash
python main.py --model mistral-small-latest
```

## 🛠 Usage
Once the agent is running, you can interact with it normally. Use these special commands:
* `/history`: Display the current conversation stored in the agent's state.
* `/reset`: Wipe the current thread memory and start a fresh session.
* `/exit`: Close the application.

## 📈 Monitoring
All traces are automatically sent to Langfuse. You can view the reasoning steps, tool outputs, and token usage by logging into your Langfuse project dashboard.