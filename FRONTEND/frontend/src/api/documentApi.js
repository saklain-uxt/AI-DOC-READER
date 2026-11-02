
import { apiRequest } from "./api";

// Upload a document to the FastAPI backend.
export const uploadDocument = async (file) => {
  const formData = new FormData();

  // The backend expects the multipart field to be named "file".
  formData.append("file", file);

  return apiRequest("/api/documents/upload", {
    method: "POST",
    body: formData,
  });
};

// Fetch all documents belonging to the logged-in user.
export const getAllDocuments = async () => {
  return apiRequest("/api/documents/");
};


// Retrieve PDF file.
export const getDocumentFile = async (documentId) => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/api/documents/${encodeURIComponent(documentId)}/file`,
    {
      method: "GET",
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error("Unable to retrieve PDF file.");
  }

  return response.blob();
};

// Fetch one document using its MongoDB ID.
export const getDocumentById = async (documentId) => {
  return apiRequest(
    `/api/documents/${encodeURIComponent(documentId)}`
  );
};

// Delete a document using its MongoDB ID.
export const deleteDocument = async (documentId) => {
  return apiRequest(
    `/api/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
    }
  );
};
