const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Document upload failed"
    );
  }

  return response.json();
}


export async function askQuestion(
  question,
  documentId,
  topK = 3
) {
  const response = await fetch(
    `${API_BASE_URL}/chat`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        question,
        document_id: documentId,
        top_k: topK,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json();

    throw new Error(
      error.detail || "Question failed"
    );
  }

  return response.json();
}