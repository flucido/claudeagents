// Researcher Agent Tools

export const researcherTools = [
  {
    name: "take_notes",
    description: "Save important information learned during the conversation",
    input_schema: {
      type: "object",
      properties: {
        topic: {
          type: "string",
          description: "The topic or subject of the note"
        },
        content: {
          type: "string",
          description: "The information to save"
        }
      },
      required: ["topic", "content"]
    }
  },
  {
    name: "generate_question",
    description: "Generate a follow-up question based on the current topic",
    input_schema: {
      type: "object",
      properties: {
        topic: {
          type: "string",
          description: "The topic to ask about"
        },
        previous_answer: {
          type: "string",
          description: "The previous answer received, to generate a relevant follow-up"
        }
      },
      required: ["topic"]
    }
  }
];

// Store notes in memory
const notes = [];

export function executeResearcherTool(toolName, toolInput) {
  switch (toolName) {
    case "take_notes":
      notes.push({
        topic: toolInput.topic,
        content: toolInput.content,
        timestamp: new Date().toISOString()
      });
      return `Note saved: ${toolInput.topic} - ${toolInput.content}`;

    case "generate_question":
      const questions = [
        `Can you explain more about ${toolInput.topic}?`,
        `What are the key aspects of ${toolInput.topic}?`,
        `How does ${toolInput.topic} work in practice?`,
        `What are some examples of ${toolInput.topic}?`
      ];
      return questions[Math.floor(Math.random() * questions.length)];

    default:
      return "Unknown tool";
  }
}

export function getResearcherNotes() {
  return notes;
}
