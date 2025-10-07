import gradio as gr
import requests
import json
import os

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:3000")

def run_agent_conversation(topic, num_turns):
    """
    Trigger the agent conversation via the Node.js backend
    """
    try:
        response = requests.post(
            f"{API_URL}/api/conversation",
            json={"topic": topic, "turns": int(num_turns)},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()

            # Format conversation
            conversation_text = ""
            for msg in data["conversation"]:
                agent = msg["agent"]
                message = msg["message"]
                emoji = "🔍" if agent == "Researcher" else "👨‍🏫"
                conversation_text += f"\n{emoji} **{agent}:**\n{message}\n\n---\n"

            # Format notes
            notes_text = "## 📝 Research Notes\n\n"
            if data["notes"]:
                for note in data["notes"]:
                    notes_text += f"**{note['topic']}**\n{note['content']}\n\n"
            else:
                notes_text += "*No notes taken yet*"

            return conversation_text, notes_text
        else:
            return f"Error: {response.status_code} - {response.text}", "Error retrieving notes"

    except requests.exceptions.ConnectionError:
        return "❌ **Error: Cannot connect to backend server**\n\nMake sure the Node.js server is running:\n```\nnpm start\n```", ""
    except Exception as e:
        return f"❌ **Error:** {str(e)}", ""

# Create Gradio interface
with gr.Blocks(title="Claude Agent Conversation", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🤖 Claude Agent Conversation Platform

        Watch two AI agents have a conversation! The **Researcher** asks questions and takes notes,
        while the **Expert** provides knowledgeable answers.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            topic_input = gr.Textbox(
                label="Topic to Explore",
                placeholder="e.g., machine learning, quantum computing, API design...",
                value="machine learning"
            )
            turns_input = gr.Slider(
                minimum=1,
                maximum=5,
                value=3,
                step=1,
                label="Number of Conversation Turns"
            )
            submit_btn = gr.Button("▶️ Start Conversation", variant="primary", size="lg")

        with gr.Column(scale=2):
            gr.Markdown("### 💬 Live Conversation")
            conversation_output = gr.Markdown(
                value="*Click 'Start Conversation' to begin...*",
                show_label=False
            )

    with gr.Row():
        with gr.Column():
            notes_output = gr.Markdown(
                value="## 📝 Research Notes\n\n*Notes will appear here after the conversation*",
                show_label=False
            )

    gr.Markdown(
        """
        ---
        ### How it works:
        1. **Researcher Agent** 🔍 - Asks curious questions and takes detailed notes
        2. **Expert Agent** 👨‍🏫 - Provides knowledgeable answers using its knowledge base
        3. They exchange ideas for the specified number of turns

        ### Requirements:
        - Node.js backend must be running (`npm start`)
        - `ANTHROPIC_API_KEY` environment variable must be set
        """
    )

    submit_btn.click(
        fn=run_agent_conversation,
        inputs=[topic_input, turns_input],
        outputs=[conversation_output, notes_output]
    )

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Claude Agent Conversation UI")
    print("="*60)
    print(f"\n📡 Backend API: {API_URL}")
    print("\n⚠️  Make sure the Node.js backend is running:")
    print("   npm start")
    print("\n🌐 Gradio UI will open in your browser...\n")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
