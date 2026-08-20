const API_BASE_URL = "http://127.0.0.1:8000/api/v1";


// =========================================
// GENERIC API REQUEST
// =========================================

async function request(url, options = {}) {

  const response = await fetch(
    `${API_BASE_URL}${url}`,
    options
  );

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {

    let errorMessage =
      data.detail ||
      data.message ||
      `Request failed (${response.status})`;

    // FastAPI validation errors
    if (Array.isArray(data.detail)) {

      errorMessage = data.detail
        .map((error) => error.msg)
        .join(", ");
    }

    throw new Error(errorMessage);
  }

  return data;
}


// =========================================
// HEALTH CHECK
// =========================================

export async function healthCheck() {

  return request("/health");
}


// =========================================
// UPLOAD DOCUMENT
// =========================================

export async function uploadDocument(file) {

  const formData = new FormData();

  formData.append(
    "file",
    file
  );

  return request(
    "/documents/upload",
    {
      method: "POST",
      body: formData,
    }
  );
}


// =========================================
// CREATE CONVERSATION
// =========================================

export async function createConversation(
  title = "New Conversation",
  documentId = null
) {

  return request(
    "/conversations",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({

        title,

        document_id:
          documentId,

      }),
    }
  );
}


// =========================================
// GET ALL CONVERSATIONS
// =========================================

export async function getConversations() {

  return request(
    "/conversations"
  );
}


// =========================================
// GET SINGLE CONVERSATION
// =========================================

export async function getConversation(
  conversationId
) {

  return request(
    `/conversations/${conversationId}`
  );
}


// =========================================
// DELETE CONVERSATION
// =========================================

export async function deleteConversation(
  conversationId
) {

  return request(
    `/conversations/${conversationId}`,
    {
      method: "DELETE",
    }
  );
}


// =========================================
// ASK QUESTION
// =========================================

export async function askQuestion(
  question,
  documentId,
  conversationId,
  topK = 3
) {

  return request(
    "/chat",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({

        question,

        document_id:
          documentId,

        conversation_id:
          conversationId,

        top_k:
          topK,

      }),
    }
  );
}