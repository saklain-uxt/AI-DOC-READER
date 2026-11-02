
import { useEffect, useState } from "react";

import { getDocumentFile } from "../api/documentApi";

export default function usePDFDocument(documentId) {

  // Stores the PDF object URL.
  const [pdfUrl, setPdfUrl] = useState(null);

  // Tracks PDF loading.
  const [loading, setLoading] = useState(true);

  // Stores any error.
  const [error, setError] = useState("");


  useEffect(() => {

    let objectUrl;

    const fetchPDF = async () => {

      try {
        setLoading(true);
        setError("");
        setPdfUrl(null);

        // Retrieve PDF using document.js
        const blob = await getDocumentFile(documentId);

        // Validate PDF.
        if (blob.type !== "application/pdf") {
          throw new Error("Invalid PDF file.");
        }

        // Convert Blob into browser-readable URL.
        objectUrl = URL.createObjectURL(blob);

        setPdfUrl(objectUrl);

      } catch (err) {

        setError(
          err.message || "Unable to load PDF document."
        );

      } finally {

        setLoading(false);

      }
    };

    if (documentId) {
      fetchPDF();
    } else {
      setError("Document ID is missing.");
      setLoading(false);
    }


    // Cleanup when component unmounts
    // or documentId changes.
    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };

  }, [documentId]);


  return {
    pdfUrl,
    loading,
    error,
  };
}
