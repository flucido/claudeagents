# Claude Agent Conversation Platform

A simple demo of two AI agents having a conversation using the Claude Agent SDK, with a Gradio web interface.

## 🤖 The Agents

### Researcher Agent 🔍
- Asks curious questions
- Takes detailed notes
- Generates follow-up questions
- Stores learning in memory

### Expert Agent 👨‍🏫
- Provides knowledgeable answers
- Has a knowledge base about various topics
- Creates summaries of complex information
- Patient and thorough in explanations

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (3.8+)
- Anthropic API key

### 1. Install Node.js Dependencies
```bash
npm install
```

### 2. Install Python Dependencies
```bash
pip install -r ui/requirements.txt
```

### 3. Set up Environment Variables
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Start the Backend Server
```bash
npm start
```

### 5. Start the Gradio UI (in a new terminal)
```bash
python ui/app.py
```

### 6. Open Your Browser
The Gradio interface will automatically open at `http://localhost:7860`

## 📖 Usage

1. Enter a topic you want the agents to discuss (e.g., "machine learning", "quantum computing")
2. Choose how many conversation turns (1-5)
3. Click "Start Conversation"
4. Watch the agents interact in real-time!
5. Review the research notes at the end

## 🏗️ Project Structure

```
claude-agents/
├── src/
│   ├── agents/
│   │   ├── researcher/
│   │   │   ├── agent.js      # Researcher agent configuration
│   │   │   └── tools.js      # Researcher tools (note-taking, questions)
│   │   └── expert/
│   │       ├── agent.js      # Expert agent configuration
│   │       └── tools.js      # Expert tools (knowledge, summaries)
│   └── orchestrator.js       # Main orchestration logic & API server
├── ui/
│   ├── app.py               # Gradio web interface
│   └── requirements.txt     # Python dependencies
├── package.json
└── README.md
```

## 🛠️ API Endpoints

### `POST /api/conversation`
Start a new agent conversation

**Request:**
```json
{
  "topic": "machine learning",
  "turns": 3
}
```

**Response:**
```json
{
  "conversation": [
    {
      "agent": "Researcher",
      "message": "I'd like to learn about machine learning..."
    },
    {
      "agent": "Expert",
      "message": "Machine learning is..."
    }
  ],
  "notes": [
    {
      "topic": "ML Definition",
      "content": "Machine learning enables systems to learn...",
      "timestamp": "2025-10-05T..."
    }
  ]
}
```

### `GET /api/health`
Health check endpoint

## 🔧 Configuration

### Adding Topics to Knowledge Base
Edit `src/agents/expert/tools.js` and add entries to the `knowledgeBase` object:

```javascript
const knowledgeBase = {
  "your-topic": "Your detailed explanation here...",
  // ... more topics
};
```

### Customizing Agents
Edit the system prompts in:
- `src/agents/researcher/agent.js`
- `src/agents/expert/agent.js`

### Adding New Tools
Add tool definitions to the respective `tools.js` files and implement the execution logic.

## 📝 Example Topics

Try these topics to see the agents in action:
- Machine learning
- Neural networks
- API design
- Quantum computing
- Cloud architecture
- Database optimization

## 🐛 Troubleshooting

**Backend won't start:**
- Make sure you have set `ANTHROPIC_API_KEY` in your `.env` file
- Check that port 3000 is available

**UI can't connect to backend:**
- Ensure the Node.js server is running (`npm start`)
- Check that the API_URL in `ui/app.py` matches your backend URL

**Agents not responding:**
- Verify your Anthropic API key is valid
- Check the terminal logs for error messages

## 🚀 Next Steps

Ideas for extending this project:
- Add more agents with different specializations
- Implement persistent storage for notes
- Add more sophisticated tools
- Create multi-agent debates or collaborations
- Add voice input/output
- Implement agent memory across sessions

## 📄 License

MIT
