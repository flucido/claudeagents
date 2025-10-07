# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Claude Agent Conversation Platform that demonstrates two AI agents (Researcher and Expert) having structured conversations using the Claude Agent SDK. The system includes a Node.js backend orchestrator and a Gradio-based Python web UI.

## Architecture

### Core Components

- **Orchestrator** (`src/orchestrator.js`): Express server that manages agent conversations and provides REST API
- **Agent System**: Two specialized agents with distinct roles and toolsets
  - **Researcher Agent** (`src/agents/researcher/`): Takes notes, asks follow-up questions
  - **Expert Agent** (`src/agents/expert/`): Provides knowledge from built-in knowledge base
- **Web UI** (`ui/app.py`): Gradio interface for interacting with the conversation system

### Agent Architecture Pattern

Each agent follows a consistent structure:
- `agent.js`: Configuration with system prompt, model selection, and tool references
- `tools.js`: Tool definitions and execution functions

Agents use Claude's function calling to access tools during conversations. The orchestrator handles tool execution and maintains conversation history.

## Development Commands

### Environment Setup
```bash
# Copy environment template and add your Anthropic API key
cp .env.example .env
# Edit .env to add ANTHROPIC_API_KEY

# Install Node.js dependencies
npm install

# Install Python dependencies  
pip install -r ui/requirements.txt
```

### Running the System
```bash
# Start backend server (development with auto-reload)
npm run dev

# Start backend server (production)
npm start

# Start web UI (in separate terminal)
python ui/app.py
```

### Development Mode
- Backend runs on http://localhost:3000 with API endpoints
- UI runs on http://localhost:7860 with auto-opening browser
- Use `npm run dev` for file watching during development

## Key Technical Details

### Agent Configuration
- Both agents use `claude-3-5-sonnet-20241022` model
- Tools are defined with JSON schemas for input validation
- Agent responses can trigger multiple tool calls in sequence
- Conversation history is maintained globally during a session

### Knowledge Base
The Expert agent uses a simple in-memory knowledge base (`src/agents/expert/tools.js`). To add topics:
```javascript
const knowledgeBase = {
  "new-topic": "Detailed explanation here...",
  // existing topics...
};
```

### API Structure
- `POST /api/conversation`: Starts conversation with `{topic, turns}` parameters
- `GET /api/health`: Health check endpoint
- Backend serves JSON responses with conversation array and researcher notes

### Memory and State
- Researcher notes stored in memory during runtime (cleared on restart)
- Conversation history maintained per session
- No persistent storage implemented

## Testing and Quality

The project includes Codacy configuration for code quality analysis:
```bash
# Run code analysis (if Codacy CLI is installed)
codacy analyze --root-path /path/to/project
```

## Common Development Tasks

### Adding New Agent Tools
1. Add tool definition to respective `tools.js` file
2. Implement execution logic in `executeAgentTool` function  
3. Update agent system prompt to reference new tool

### Extending Knowledge Base
Modify `knowledgeBase` object in `src/agents/expert/tools.js` with new topic entries.

### Modifying Agent Behavior
Update system prompts in `src/agents/*/agent.js` files to change agent personalities or instructions.