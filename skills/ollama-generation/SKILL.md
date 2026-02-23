---
name: ollama-generation
description: "Instructions for generating answers using Ollama and Gemma3."
---

# Ollama Generation Skill

## Goal
Generate natural language answers based on retrieved context using a local Ollama instance running Gemma3.

## API Usage
- **Endpoint**: `http://localhost:11434/api/chat`
- **Model**: `gemma3`

## Prompt Design
Provide the retrieved context clearly to the model.

```json
{
  "model": "gemma3",
  "messages": [
    {
      "role": "system",
      "content": "あなたは親切なアシスタントです。提供されたコンテキスト情報のみに基づいて質問に答えてください。"
    },
    {
      "role": "user",
      "content": "Context:\n{context}\n\nQuestion: {query}"
    }
  ],
  "stream": false
}
```

## Implementation Notes
- Handle timeouts gracefully.
- If the context is too long, consider truncating it or selecting the most relevant snippets.
- Ensure the Ollama service is running locally before sending requests.
