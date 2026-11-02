
import { useRef, useState } from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { useDocumentStore } from "../../store/documentStore";

export default function UploadArea() {
  const fileInputRef = useRef(null);

  const uploadFile = useDocumentStore((state) => state.uploadFile);
  const uploading = useDocumentStore((state) => state.uploading);

  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  // Handle PDF selection.
  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    setMessage("");

    // Validate file type.
    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setMessage("Please select a PDF file.");
      setIsError(true);
      setSelectedFile(null);
      event.target.value = "";
      return;
    }

    // Maximum file size: 10 MB.
    if (file.size > 10 * 1024 * 1024) {
      setMessage("File size must not exceed 10 MB.");
      setIsError(true);
      setSelectedFile(null);
      event.target.value = "";
      return;
    }

    setSelectedFile(file);
    setIsError(false);
  }

  // Upload the selected PDF.
  async function handleUpload() {
    if (!selectedFile) return;

    setMessage("");

    try {
      await uploadFile(selectedFile);

      setMessage("Document uploaded successfully!");
      setIsError(false);
      setSelectedFile(null);
      fileInputRef.current.value = "";
    } catch (error) {
      setMessage(error.message || "Upload failed.");
      setIsError(true);
    }
  }

  // Clear the selected file.
  function handleRemoveFile() {
    setSelectedFile(null);
    fileInputRef.current.value = "";
    setMessage("");
  }

  return (
    <section className="content-card">
      <div className="section-heading">
        <div>
          <h2>Upload Document</h2>
          <p className="muted">
            Add a PDF to your personal knowledge hub.
          </p>
        </div>

        <UploadCloud size={22} />
      </div>

      <div className="upload-area">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          hidden
          onChange={handleFileChange}
        />

        <UploadCloud size={36} />

        <h3>Select your PDF document</h3>

        <p className="muted">Maximum file size: 10 MB</p>

        <button
          className="primary-btn compact-btn"
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          Choose PDF
        </button>

        {selectedFile && (
          <div className="selected-file">
            <FileText size={18} />
            <span>{selectedFile.name}</span>

            <button
              type="button"
              onClick={handleRemoveFile}
              disabled={uploading}
              aria-label="Remove selected file"
            >
              <X size={16} />
            </button>
          </div>
        )}

        {selectedFile && (
          <button
            className="primary-btn compact-btn"
            type="button"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload Document"}
          </button>
        )}

        {message && (
          <p role="status" style={{ color: isError ? "#ef4444" : "#22c55e" }}>
            {message}
          </p>
        )}
      </div>
    </section>
  );
}
