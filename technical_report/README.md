# Technical Report

## Key Design Decisions

- **Multi-stage workflow**: responses are gathered, then reviewed, then synthesized to reduce single-model bias.
- **Model anonymity during review**: prevents preference bias in cross-evaluation.
- **Parallel querying**: models are called concurrently to keep latency acceptable.
- **Local LLM hosting with Ollama**: avoids external API dependencies and keeps data local.
- **Simple storage**: conversation history stored as JSON for easy inspection and debugging.

## Chosen LLM Models

Configured in `backend/config.py`:

- Chairman: `qwen2.5:1.5b`
- Councilor: `llama3.2:3b`
- Councilor: `llama3.2:1b`

