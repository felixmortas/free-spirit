# 🤖 ReAct Agent Chatbot

A robust, terminal-based conversational agent built with **LangChain** and **LangGraph**. This project implements a ReAct (Reasoning and Acting) loop, allowing the agent to use custom tools, maintain conversation memory via a persistent checkpointer, and track all operations through **Langfuse**.

## ✨ Features

-   **ReAct Logic**: The agent doesn't just chat; it reasons about which tools to use to solve complex queries.
-   **Short-term Memory**: Uses LangGraph `Checkpointers` to maintain context across a conversation thread.
-   **Observability**: Full integration with Langfuse to monitor latency, costs, and traces.
-   **Resilience**: Middleware support for model fallbacks if the primary LLM provider is down.
-   **Terminal Commands**: Built-in commands like `/reset` to clear history and `/history` to view the log.
-   **RAG Tooling**: The agent can search a Redis vector database populated by the ingestion pipeline to answer domain-specific questions.

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

## 🧰 Agent Tools

The agent uses a **ReAct loop** to decide when and which tools to invoke based on the user's query. Tools are defined in `tools.py` and automatically made available to the agent at startup.

### Available Tools

#### `search_knowledge_base`
Performs a semantic search over a Redis vector database populated by the ingestion pipeline. The agent uses this tool to answer questions about internal information such as services, policies, amenities, and rates.

- **Input**: A natural-language query string.
- **Output**: The most relevant text excerpts from the knowledge base, ranked by similarity score.
- **Threshold**: Only results with a similarity score ≥ `0.5` are returned.

You can extend the agent by adding new tools to the `get_tools()` function in `tools.py`.

## 🗄 Ingestion Pipeline

Before the agent can search the knowledge base, you need to populate it by crawling a website and indexing its content into Redis. This is handled by the ingestion pipeline, which you run via the `cli.py` script.

### How It Works

The pipeline (`pipeline.py`) runs through the following steps:

1. **Crawl** — Fetches all pages from the given URL using `SimpleCrawler`.
2. **Clean** — Strips HTML tags and extracts meaningful text with `HtmlCleaner`.
3. **Filter** — Keeps only pages relevant to the domain (currently filters for pages mentioning `"ecuador"` in the first line).
4. **Deduplicate** — Removes boilerplate lines that repeat across pages using `BoilerplateFilter`.
5. **Chunk** — Splits the merged text into smaller segments with `LangchainChunker`.
6. **Embed** — Converts each chunk into a vector using `MistralEmbedder`.
7. **Store** — Saves the chunks and their vectors into `RedisVectorDB`.

### Running the Ingestion CLI

```bash
python cli.py <URL>
```

**Options:**

| Flag | Description |
|---|---|
| `--flush` | Deletes all existing data in Redis before running the pipeline. Use this to start fresh. |

**Examples:**

```bash
# Index a website
python cli.py https://www.example-hostel.com

# Wipe the database and re-index from scratch
python cli.py https://www.example-hostel.com --flush
```

Intermediate files are saved locally for inspection:
- `data/raw/page_N.html` — Raw HTML of each crawled page.
- `data/clean/page_N.txt` — Cleaned text of each kept page.
- `data/merged.txt` — Final deduplicated and merged text before chunking.

## 📈 Monitoring
All traces are automatically sent to Langfuse. You can view the reasoning steps, tool outputs, and token usage by logging into your Langfuse project dashboard.