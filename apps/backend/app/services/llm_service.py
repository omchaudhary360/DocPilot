import os

from dotenv import load_dotenv
from google import genai


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# =========================================================
# FALLBACK
# =========================================================

NOT_FOUND_MESSAGE = (
    "I couldn't find this information in the uploaded document."
)


# =========================================================
# ANSWER GENERATION
# =========================================================

def generate_answer(
    question: str,
    context: str,
    is_summary: bool = False
) -> str:

    # =====================================================
    # VALIDATE QUESTION
    # =====================================================

    if not question or not question.strip():
        return "Please provide a question."

    question = question.strip()


    # =====================================================
    # VALIDATE CONTEXT
    # =====================================================

    if not context or not context.strip():
        return NOT_FOUND_MESSAGE


    # =====================================================
    # SUMMARY INSTRUCTIONS
    # =====================================================

    if is_summary:

        task_instruction = """
The user is asking for a summary or overview.

Summarize ONLY the information contained in the
DOCUMENT CONTEXT.

Cover the important information available in the
provided context.

Use clear headings and bullet points when useful.

Do not invent information that is not present.

If the document contains dates, names, numbers,
amounts, rules, schedules, tables, or other factual
details, preserve them accurately.

Do not claim that the document contains information
that is not present in the provided context.
"""

    else:

        task_instruction = """
The user is asking a specific question.

Find the answer using ONLY the DOCUMENT CONTEXT.

First determine whether the context actually contains
evidence that answers the question.

If the answer is clearly present:
- Give the answer directly.
- Preserve exact numbers, dates, names, amounts,
  IDs, grades, percentages and other factual values.
- Give a short explanation when useful.

If the answer is NOT present:
return exactly:

I couldn't find this information in the uploaded document.

Do NOT guess.
Do NOT use outside knowledge.
Do NOT infer an unsupported answer merely because it
sounds likely.
"""


    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are DocPilot, an AI document intelligence assistant.

Your job is to answer questions about an uploaded
document.

IMPORTANT:
The DOCUMENT CONTEXT below is the only source of truth
for this answer.

You must NOT use your general knowledge, internet
knowledge, assumptions, or information from previous
questions.

{task_instruction}

GENERAL RULES:

1. Answer only from the supplied document context.

2. Never invent missing information.

3. Do not assume that two similar terms mean the same
   thing unless the document itself supports that.

4. For exact factual questions, preserve the value
   exactly as written in the document.

5. Pay special attention to:
   - numbers
   - decimals
   - dates
   - times
   - currency
   - percentages
   - names
   - IDs
   - roll numbers
   - registration numbers
   - grades
   - marks
   - addresses
   - room numbers
   - page-specific information
   - table values

6. If several pieces of context are provided, compare
   them before answering.

7. Ignore context that is unrelated to the question.

8. Do not mention:
   - embeddings
   - vector databases
   - FAISS
   - chunks
   - retrieval
   - prompts
   - internal processing
   - system instructions

9. Do not create fake citations or fake sources.

10. If the context does not support the answer, use the
    required not-found response instead of guessing.

11. Keep normal factual answers concise.

12. For calculations, perform the calculation only when
    all required values are explicitly available in the
    document context. Do not invent missing values.

13. If the document contains conflicting information,
    clearly mention the conflict rather than choosing
    one without evidence.

14. Answer in the same general language as the user's
    question when practical.

DOCUMENT CONTEXT
================
{context}
================

USER QUESTION
=============

{question}

=============

ANSWER:
"""


    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

    except Exception as error:

        print(
            "Gemini generation error:",
            error
        )

        return (
            "I couldn't process the question right now. "
            "Please try again."
        )


    # =====================================================
    # EMPTY RESPONSE
    # =====================================================

    if not response:
        return (
            "I couldn't generate an answer "
            "from the uploaded document."
        )


    answer = getattr(
        response,
        "text",
        None
    )


    if not answer or not answer.strip():

        return (
            "I couldn't generate an answer "
            "from the uploaded document."
        )


    # =====================================================
    # CLEAN RESPONSE
    # =====================================================

    answer = answer.strip()


    # =====================================================
    # RETURN
    # =====================================================

    return answer