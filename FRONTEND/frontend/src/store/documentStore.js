
import { create } from "zustand";

import {
  uploadDocument,
  getAllDocuments,
  deleteDocument,
} from "../api/documentApi";

export const useDocumentStore = create((set, get) => ({
  // Stores all documents fetched from the backend.
  documents: [],

  // Tracks whether documents are being fetched.
  loading: false,

  // Tracks whether a file is currently uploading.
  uploading: false,

  // Stores API error messages.
  error: null,

  // Fetch all documents belonging to the logged-in user.
  fetchDocuments: async () => {
    set({ loading: true, error: null });

    try {
      const response = await getAllDocuments();

      // Backend returns: { documents: [...], total: number }
      set({
        documents: response.documents || [],
        loading: false,
      });

      return response;
    } catch (error) {
      set({
        error: error.message,
        loading: false,
      });

      throw error;
    }
  },

  // Upload a new document.
  uploadFile: async (file) => {
    set({ uploading: true, error: null });

    try {
      const response = await uploadDocument(file);

      // Refresh the document list after successful upload.
      await get().fetchDocuments();

      set({ uploading: false });

      return response;
    } catch (error) {
      set({
        error: error.message,
        uploading: false,
      });

      throw error;
    }
  },

  // Delete a document using its ID.
removeDocument: async (documentId) => {
  console.log("1. Delete function called:", documentId);

  set({ error: null });

  try {
    console.log("2. Sending DELETE API request");

    const response = await deleteDocument(documentId);

    console.log("3. Backend response:", response);

    set((state) => ({
      documents: state.documents.filter(
        (document) => document.id !== documentId
      ),
    }));

    console.log("4. Document removed from Zustand");

    return response;

  } catch (error) {
    console.error("Delete error:", error);

    set({ error: error.message });
    throw error;
  }
},

  // Clear previous errors.
  clearError: () => set({ error: null }),
}));
