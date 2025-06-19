# 🎓 GraLLM-Tutor: A Framework for Explainable AI Answers

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://[huggingface.co/spaces/jaisal2000/Conceptual-LLM-Tutor])

This project demonstrates a system that makes AI-generated answers more trustworthy and understandable by revealing the reasoning behind them.

### The Goal: Making AI Answers Trustworthy

Large Language Models (LLMs) are powerful but often act like "black boxes," giving answers without explaining how they got there. This makes it difficult to trust or learn from them.

**GraLLM-Tutor** is a proof-of-concept that tackles this problem. It combines two powerful AI technologies to:
1.  **Get a fluent answer** from a modern LLM.
2.  **Explain the "why"** using a structured commonsense knowledge graph.

---

### How It Works

The system uses a simple but powerful pipeline to generate an answer and then explain it.

**Example Interaction:**

**User:** `Why do we use sunscreen?`

**LLM Answer:**
> We use sunscreen to protect our skin from harmful ultraviolet (UV) rays from the sun.

**ConceptNet-Grounded Explanation:**
> This makes sense because the sun is known to emit ultraviolet rays, which in turn can cause skin damage. Sunscreen is a product specifically used for protecting skin, providing a barrier against this damage.

This explanation is automatically built from verifiable relationships found in ConceptNet, such as:
*   `"sun"` **Emits** `"ultraviolet_rays"`
*   `"ultraviolet_rays"` **Causes** `"skin_damage"`
*   `"sunscreen"` **UsedFor** `"protecting_skin"`


---

### Technology & Live Demo

This application is built with freely available tools and is deployed for public use.

*   **Language Model:** `Llama 3` via the Groq API.
*   **Knowledge Graph:** `ConceptNet 5.7` via its public API.
*   **UI & Deployment:** `Gradio` and `Hugging Face Spaces`.

#### >> [Try the Live Demo Here](https://[huggingface.co/spaces/jaisal2000/Conceptual-LLM-Tutor]) <<

---

### Limitations and Future Directions

This is an early-stage prototype with clear areas for improvement:
*   **Knowledge Gaps:** The explanation quality depends on the completeness of ConceptNet's knowledge base.
*   **Concept Extraction:** The system's effectiveness relies on accurately identifying the most important concepts from the text.
*   **Deeper Reasoning:** Explanations are currently based on direct, single-step links. Future work could explore multi-step reasoning for more complex questions.