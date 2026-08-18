from app.services.llm_service import generate_answer


context = """
The project objective is to allow users to upload documents,
automatically process and understand document content,
store document embeddings in a vector database,
enable natural language querying of uploaded documents,
and generate accurate answers grounded in document content.
"""


question = "What is the objective of this project?"


answer = generate_answer(
    question=question,
    context=context
)


print("\nAnswer:")
print(answer)