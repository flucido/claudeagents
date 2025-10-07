import 'dotenv/config';
import Anthropic from '@anthropic-ai/sdk';
import { researcherConfig } from './agents/researcher/agent.js';
import { expertConfig } from './agents/expert/agent.js';
import { getResearcherNotes } from './agents/researcher/tools.js';
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

// Conversation state
let conversationHistory = [];

async function runAgentTurn(agentConfig, userMessage) {
  const messages = [
    ...conversationHistory,
    { role: "user", content: userMessage }
  ];

  let response = await anthropic.messages.create({
    model: agentConfig.model,
    max_tokens: 1024,
    system: agentConfig.systemPrompt,
    tools: agentConfig.tools,
    messages: messages
  });

  console.log(`\n[${agentConfig.name}] Initial response:`, response.content);

  // Handle tool calls
  while (response.stop_reason === "tool_use") {
    const toolUse = response.content.find(block => block.type === "tool_use");

    if (!toolUse) break;

    console.log(`\n[${agentConfig.name}] Using tool: ${toolUse.name}`);
    console.log(`Tool input:`, toolUse.input);

    const toolResult = agentConfig.executeToolFunction(toolUse.name, toolUse.input);
    console.log(`Tool result:`, toolResult);

    messages.push({ role: "assistant", content: response.content });
    messages.push({
      role: "user",
      content: [{
        type: "tool_result",
        tool_use_id: toolUse.id,
        content: toolResult
      }]
    });

    response = await anthropic.messages.create({
      model: agentConfig.model,
      max_tokens: 1024,
      system: agentConfig.systemPrompt,
      tools: agentConfig.tools,
      messages: messages
    });

    console.log(`\n[${agentConfig.name}] Response after tool:`, response.content);
  }

  // Extract text response
  const textContent = response.content.find(block => block.type === "text");
  const agentResponse = textContent ? textContent.text : "No response";

  // Update conversation history with all messages (including tool use/results)
  conversationHistory = messages.slice();
  conversationHistory.push({ role: "assistant", content: response.content });

  return agentResponse;
}

async function runConversation(initialTopic, turns = 3) {
  conversationHistory = [];
  const conversation = [];

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Starting conversation about: ${initialTopic}`);
  console.log('='.repeat(60));

  // Researcher starts with a question
  let currentMessage = `I'd like to learn about ${initialTopic}. Can you teach me about it?`;
  conversation.push({ agent: "Researcher", message: currentMessage });

  for (let i = 0; i < turns; i++) {
    console.log(`\n--- Turn ${i + 1} ---`);

    // Expert responds
    console.log(`\n[Researcher → Expert]: ${currentMessage}`);
    const expertResponse = await runAgentTurn(expertConfig, currentMessage);
    console.log(`\n[Expert]: ${expertResponse}`);
    conversation.push({ agent: "Expert", message: expertResponse });

    if (i < turns - 1) {
      // Researcher asks follow-up
      const researcherResponse = await runAgentTurn(
        researcherConfig,
        `The expert said: "${expertResponse}". What should I ask next?`
      );
      console.log(`\n[Researcher]: ${researcherResponse}`);
      conversation.push({ agent: "Researcher", message: researcherResponse });
      currentMessage = researcherResponse;
    }
  }

  // Get final notes
  const notes = getResearcherNotes();
  console.log(`\n${'='.repeat(60)}`);
  console.log('Researcher Notes:');
  console.log('='.repeat(60));
  notes.forEach(note => {
    console.log(`📝 ${note.topic}: ${note.content}`);
  });

  return { conversation, notes };
}

// API endpoints
app.post('/api/conversation', async (req, res) => {
  try {
    const { topic, turns } = req.body;
    const result = await runConversation(topic, turns || 3);
    res.json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`\n🚀 Agent Orchestrator running on http://localhost:${PORT}`);
    console.log(`\nAPI Endpoints:`);
    console.log(`  POST /api/conversation - Start a new conversation`);
    console.log(`  GET  /api/health - Health check\n`);
  });
}

export { app, runConversation };
