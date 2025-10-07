// Expert Agent Tools

export const expertTools = [
  {
    name: "retrieve_knowledge",
    description: "Retrieve detailed knowledge about a specific topic from the knowledge base",
    input_schema: {
      type: "object",
      properties: {
        topic: {
          type: "string",
          description: "The topic to retrieve information about"
        }
      },
      required: ["topic"]
    }
  },
  {
    name: "create_summary",
    description: "Create a concise summary of complex information",
    input_schema: {
      type: "object",
      properties: {
        content: {
          type: "string",
          description: "The content to summarize"
        },
        length: {
          type: "string",
          enum: ["brief", "moderate", "detailed"],
          description: "How detailed the summary should be"
        }
      },
      required: ["content"]
    }
  }
];

// Simulated knowledge base
const knowledgeBase = {
  "machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data and make decisions with minimal human intervention.",

  "neural networks": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) organized in layers that process information using a connectionist approach to computation.",

  "api design": "API design is the process of creating application programming interfaces that are intuitive, efficient, and maintainable. Good API design follows principles like consistency, simplicity, and clear documentation.",

  "quantum computing": "Quantum computing uses quantum-mechanical phenomena like superposition and entanglement to perform computations. Unlike classical computers that use bits, quantum computers use quantum bits (qubits) that can exist in multiple states simultaneously.",

  "default": "This is a fascinating topic that involves understanding complex systems and their interactions. It requires careful analysis and consideration of multiple factors."
};

export function executeExpertTool(toolName, toolInput) {
  switch (toolName) {
    case "retrieve_knowledge":
      const topic = toolInput.topic.toLowerCase();
      // Find the best matching topic in knowledge base
      for (const [key, value] of Object.entries(knowledgeBase)) {
        if (topic.includes(key) || key.includes(topic)) {
          return value;
        }
      }
      return knowledgeBase.default;

    case "create_summary":
      const content = toolInput.content;
      const length = toolInput.length || "moderate";

      if (length === "brief") {
        return content.split('.')[0] + '.';
      } else if (length === "detailed") {
        return content;
      } else {
        const sentences = content.split('.');
        return sentences.slice(0, Math.ceil(sentences.length / 2)).join('.') + '.';
      }

    default:
      return "Unknown tool";
  }
}
