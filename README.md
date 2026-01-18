# LLM Council

![llmcouncil](header.jpg)

 **Group member**: Noufel BOUCHENEB


## Project Overview

LLM Council is a local web application designed to demonstrate a multi-LLM orchestration architecture.
Instead of relying on a single language model, the system distributes a user query across multiple LLMs, gathers their independent responses, and then consolidates them into a single, higher-quality answer.

The application follows a three-stage decision workflow:

1. **First opinions :** 
Each council model receives the user question and generates an answer independently, without influence from the others.

2. **Review :**
The models are then shown anonymized answers from their peers and asked to rank them based on accuracy and completeness.

3. **Final response :**  
A designated Chairman model analyzes the rankings and responses, and produces a final consolidated answer presented to the user.

### This approach aims to :

- Reduce single-model bias
- Improve answer completeness and robustness
- Demonstrate collaborative reasoning between multiple LLMs
- The entire system runs locally, relying on self-hosted LLMS models like Ollama.

## Setup and Installation Instructions

### Prerequisites

- Docker (with Docker Compose)
- A machine capable of running local LLMs (CPU sufficient)
- Internet access (only for initial model download)

### Model Configuration
 
Models and roles can be modified by editing this file : backend/config.py

**Example :** 

```js
COUNCIL_MODELS = [
    CouncilModel(ip="ollama", model_name="qwen2.5:1.5b", role=Role.CHAIRMAN),
    CouncilModel(ip="ollama", model_name="llama3.2:3b", role=Role.COUNCILOR),
    CouncilModel(ip="ollama", model_name="llama3.2:1b", role=Role.COUNCILOR),
]
```    

## Instructions to Run the Demo

### Docker Compose

Clone the github repository :

```bash
git clone https://github.com/Nouf-Nouf/llm-council-GEN-AI.git
cd llm-council-GEN-AI
```
From the project root directory:

```bash
docker compose up --build
```

## Project Structure

```text
llm-council-GEN-AI/
├─ backend/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ council.py
│  ├─ Dockerfile
│  ├─ main.py
│  ├─ models.py
│  ├─ openrouter.py
│  ├─ requirements.txt
│  └─ storage.py
├─ frontend/
│  ├─ public/
│  │  └─ vite.svg
│  ├─ src/
│  │  ├─ assets/
│  │  │  └─ react.svg
│  │  ├─ components/
│  │  │  ├─ ChatInterface.css
│  │  │  ├─ ChatInterface.jsx
│  │  │  ├─ Sidebar.css
│  │  │  ├─ Sidebar.jsx
│  │  │  ├─ Stage1.css
│  │  │  ├─ Stage1.jsx
│  │  │  ├─ Stage2.css
│  │  │  ├─ Stage2.jsx
│  │  │  ├─ Stage3.css
│  │  │  └─ Stage3.jsx
│  │  ├─ api.js
│  │  ├─ App.css
│  │  ├─ App.jsx
│  │  ├─ index.css
│  │  ├─ main.jsx
│  │  └─ ThemeContext.jsx
│  ├─ .gitignore
│  ├─ Dockerfile
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package.json
│  ├─ package-lock.json
│  └─ vite.config.js
├─ technical_report/
│  └─ README.md
├─ .gitignore
├─ .python-version
├─ docker-compose.yml
├─ header.jpg
├─ main.py
├─ pyproject.toml
└─  README.md


