import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  FileText,
  Trash2,
  RefreshCw,
  FolderOpen,
  CalendarDays,
  HardDrive,
} from "lucide-react";

import { useDocumentStore } from "../../store/documentStore";

// Convert bytes into KB or MB.
function formatFileSize(bytes) {
  if (!bytes) return "0 KB";

  const kb = bytes / 1024;

  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }

  return `${(kb / 1024).toFixed(2)} MB`;
}

// Format the uploaded date.
function formatDate(date) {
  if (!date) return "Unknown date";

  return new Date(date).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function DocumentList() {
  
const navigate = useNavigate();
  

  // Zustand state
  const documents = useDocumentStore((state) => state.documents);

  const loading = useDocumentStore((state) => state.loading);

  const error = useDocumentStore((state) => state.error);

  const fetchDocuments = useDocumentStore((state) => state.fetchDocuments);

  const removeDocument = useDocumentStore((state) => state.removeDocument);

  // Tracks which document is being deleted.
  const [deletingId, setDeletingId] = useState(null);

  // Fetch documents when the component mounts.
  useEffect(() => {
    fetchDocuments().catch(() => {});
  }, [fetchDocuments]);

  // Handle document deletion.
  async function handleDelete(documentId, filename) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?\n\nThis action cannot be undone.`,
    );

    if (!confirmed) return;

    setDeletingId(documentId);

    try {
      await removeDocument(documentId);
    } catch (error) {
      console.error("Document deletion failed:", error);
    } finally {
      setDeletingId(null);
    }
  }

  // Refresh document list.
  async function handleRefresh() {
    try {
      await fetchDocuments();
    } catch (error) {
      console.error("Unable to refresh documents:", error);
    }
  }

  return (
    <section className="content-card" id="my-documents">
      {/* Heading */}
      <div className="section-heading">
        <div>
          <h2>My Documents</h2>

          <p className="muted">Manage your uploaded PDF documents.</p>
        </div>

        <button
          className="icon-btn"
          type="button"
          onClick={handleRefresh}
          disabled={loading}
          title="Refresh documents"
          aria-label="Refresh documents"
        >
          <RefreshCw size={18} className={loading ? "spin" : ""} />
        </button>
      </div>

      {/* Error message */}
      {error && (
        <p className="document-error" role="alert">
          {error}
        </p>
      )}

      {/* Loading state */}
      {loading ? (
        <div className="empty-state">
          <RefreshCw size={28} className="spin" />
          <p>Loading your documents...</p>
        </div>
      ) : documents.length === 0 ? (
        /* Empty state */
        <div className="empty-state">
          <div className="empty-icon">
            <FolderOpen size={28} />
          </div>

          <h3>No documents yet</h3>

          <p className="muted">Upload your first PDF to get started.</p>
        </div>
      ) : (
        /* Document list */
        <div className="document-list">
          {documents.map((document) => (
            <article className="document-item" key={document.id}>
              {/* PDF icon */}
              <div className="document-icon">
                <FileText size={22} />
              </div>

              {/* Document information */}
              <div className="document-info">
                <button
                  type="button"
                  className="document-filename"
                  title={`Preview ${document.filename}`}
                  onClick={() => navigate(`/documents/${document.id}`)}
                >
                  {document.filename}
                </button>

                <div className="document-meta">
                  <span>
                    <HardDrive size={13} />
                    {formatFileSize(document.file_size)}
                  </span>

                  <span>
                    <CalendarDays size={13} />
                    {formatDate(document.created_at)}
                  </span>
                </div>

                <span className="document-status">
                  {document.status || "Uploaded"}
                </span>
              </div>

              {/* Delete button */}
              <button
                className="icon-btn delete-btn"
                type="button"
                onClick={() => handleDelete(document.id, document.filename)}
                disabled={deletingId !== null}
                title="Delete document"
                aria-label={`Delete ${document.filename}`}
              >
                {deletingId === document.id ? (
                  <RefreshCw size={18} className="spin" />
                ) : (
                  <Trash2 size={18} />
                )}
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
