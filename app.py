# --- 1. IMPORTS AND CONFIGURATION ---
# REMOVED: !pip install gradio (This is handled by requirements.txt)
import os
import requests
import json
from groq import Groq
import gradio as gr

# --- CORRECTED API KEY HANDLING for Hugging Face Spaces ---
try:
    # On Hugging Face, secrets are stored as environment variables
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    if not GROQ_API_KEY:
        raise ValueError("CRITICAL ERROR: The GROQ_API_KEY secret is not set in your Space's settings.")
    client = Groq(api_key=GROQ_API_KEY)
    print("Groq client configured successfully.")
except Exception as e:
    # This will now display a helpful error in the logs if the secret is missing.
    print(f"Error configuring Groq client: {e}")
    # We can also raise the error to stop the app from running without a key.
    raise e


# Constants
LLM_MODEL = 'llama3-8b-8192'
CONCEPTNET_API_URL = "http://api.conceptnet.io"

# --- 2. BACKEND FUNCTIONS (Unchanged) ---
def get_llm_answer(question):
    """Generates a direct, fluent answer to the user's question."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful tutor. Answer the user's question clearly and concisely."},
                {"role": "user", "content": question}
            ],
            model=LLM_MODEL, temperature=0.7)
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in get_llm_answer: {e}")
        return "Sorry, I couldn't generate an answer at the moment. The AI service might be down."

def extract_concepts_with_llm(question, answer):
    """Uses an LLM to extract key concepts."""
    prompt = f"""
From the following user question and AI answer, extract the most important concepts.
A concept should be one or two words. Return a JSON object with two keys: "question_concepts" and "answer_concepts".

Question: "{question}"
Answer: "{answer}"

Output:
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=LLM_MODEL,
            response_format={"type": "json_object"})
        concepts = json.loads(chat_completion.choices[0].message.content)
        concepts['question_concepts'] = [c.lower().replace(' ', '_') for c in concepts.get('question_concepts', [])]
        concepts['answer_concepts'] = [c.lower().replace(' ', '_') for c in concepts.get('answer_concepts', [])]
        return concepts
    except Exception as e:
        print(f"Error in extract_concepts_with_llm: {e}")
        return {"question_concepts": [], "answer_concepts": []}

def find_conceptnet_path(start_concept, end_concept):
    """Finds a relationship path between two concepts."""
    start_uri, end_uri = f"/c/en/{start_concept}", f"/c/en/{end_concept}"
    try:
        response = requests.get(f"{CONCEPTNET_API_URL}/query?start={start_uri}&end={end_uri}&limit=2")
        data = response.json()
        if data['edges']:
            edge = data['edges'][0]
            return f'"{start_concept}" {edge["rel"]["label"]} "{end_concept}"'
    except Exception as e:
        pass
    return None

def build_and_refine_explanation(question, relations):
    """Uses an LLM to build a natural language explanation."""
    if not relations: return "Could not find any commonsense relationships to build an explanation."
    structured_explanation = "\n- ".join(relations)
    prompt = f"""
Given a user's question and a set of commonsense relationships, synthesize them into a single, easy-to-understand paragraph that explains the reasoning.

User Question: "{question}"
Commonsense Relationships:
- {structured_explanation}

Generated Explanation:
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=LLM_MODEL, temperature=0.5)
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in build_and_refine_explanation: {e}")
        return "Sorry, I couldn't refine the explanation."


# --- 3. THE MAIN PIPELINE FUNCTION FOR GRADIO (Unchanged) ---
def run_tutor_pipeline(user_question):
    """
    This is the core function that Gradio will call.
    It takes a question and returns the answer and the explanation.
    """
    if not user_question:
        return "Please enter a question.", ""
        
    print(f"Processing question: {user_question}")
    llm_answer = get_llm_answer(user_question)
    concepts = extract_concepts_with_llm(user_question, llm_answer)
    if not concepts['question_concepts'] or not concepts['answer_concepts']:
        return llm_answer, "Could not extract sufficient concepts to build an explanation."

    found_relations = []
    all_concepts = list(set(concepts['question_concepts'] + concepts['answer_concepts']))
    for i in range(len(all_concepts)):
        for j in range(i + 1, len(all_concepts)):
            path = find_conceptnet_path(all_concepts[i], all_concepts[j])
            if path and path not in found_relations:
                found_relations.append(path)
                
    if not found_relations:
        final_explanation = "Could not find relevant commonsense relationships in ConceptNet for the extracted concepts."
    else:
        final_explanation = build_and_refine_explanation(user_question, found_relations)

    return llm_answer, final_explanation


# --- 4. CREATE AND LAUNCH THE GRADIO INTERFACE (Unchanged) ---
examples = [
    ["Why do we use sunscreen?"],
    ["Why should I drink water when I exercise?"],
    ["Why is it important to get enough sleep?"],
    ["Why can't you see the stars during the day?"]
]

with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown(
        """
        # 🎓 Explainable AI Tutor: GraLLM-Tutor
        Enter a "why" question to get an answer from a Large Language Model (LLM) and a step-by-step explanation grounded in the ConceptNet commonsense knowledge graph.
        """
    )
    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., Why is the sky blue?"
        )
    submit_btn = gr.Button("Get Explanation", variant="primary")
    with gr.Row():
        llm_output = gr.Textbox(label="🤖 LLM Answer", lines=5, interactive=False)
        explanation_output = gr.Textbox(label="🧠 ConceptNet-Grounded Explanation", lines=8, interactive=False)
    gr.Examples(examples, inputs=question_input)
    submit_btn.click(fn=run_tutor_pipeline, inputs=question_input, outputs=[llm_output, explanation_output])

# The launch command is slightly different for permanent deployment
iface.launch()