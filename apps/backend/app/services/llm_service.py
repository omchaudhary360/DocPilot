import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured in environment")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = os.getenv("LLM_MODEL", "gemini-2.0-flash")

NOT_FOUND_MESSAGE = (
    "I couldn't find this information in the uploaded document."
)


def generate_answer(
    question: str,
    context: str,
    is_summary: bool = False
) -> str:
    """
    Generate answer using Gemini LLM.
    
    Parameters:
    - question: User's question
    - context: Retrieved document chunks
    - is_summary: Whether this is a summary request
    
    Returns: Generated answer
    """
    
    # Validate inputs
    if not question or not question.strip():
        return "Please provide a question."
    
    question = question.strip()
    
    if not context or not context.strip():
        return NOT_FOUND_MESSAGE
    
    # Task-specific instructions
    if is_summary:
        task_instruction = """
The user is asking for a summary or overview of the document.

Summarize ONLY the information contained in the provided DOCUMENT CONTEXT.

Include the important information, facts, numbers, names, dates, and details present in the context.

Use clear formatting with headings and bullet points when appropriate.

Do not invent information that is not present in the context.

Preserve exact values for numbers, dates, names, amounts, and other factual details.
"""
    else:
        task_instruction = """
The user is asking a specific question about the document.

Use ONLY the provided DOCUMENT CONTEXT to answer.

Before answering, determine whether the context actually contains evidence for the answer.

If the answer is clearly present in the context:
- Provide the answer directly
- Preserve exact numbers, dates, names, amounts, IDs, grades, percentages, and other factual values
- Be concise

If the answer is NOT in the context:
Return EXACTLY this message:
"I couldn't find this information in the uploaded document."

Do NOT guess.
Do NOT use outside knowledge.
Do NOT infer unsupported answers.
"""
    
    # Build prompt
    prompt = f"""You are DocPilot, an AI document intelligence assistant.

Your task is to answer questions about uploaded documents using ONLY the provided context.

CRITICAL RULES:
1. Answer ONLY from the document context provided below
2. NEVER use your general knowledge or external information
3. NEVER invent facts or details not in the context
4. For factual questions: preserve exact values as written
5. For unclear information: respond with the not-found message
6. Do not mention: embeddings, vectors, FAISS, chunks, retrieval, prompts, or system details

{task_instruction}

=====================================
DOCUMENT CONTEXT
=====================================

{context}

=====================================
USER QUESTION
=====================================

{question}

=====================================
ANSWER:
"""
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
    except Exception as error:
        print(f"Gemini API error: {error}")
        return "I couldn't process the question right now. Please try again."
    
    if not response:
        return "I couldn't generate an answer from the document."
    
    answer = getattr(response, "text", None)
    
    if not answer or not answer.strip():
        return "I couldn't generate an answer from the document."
    
    return answer.strip()