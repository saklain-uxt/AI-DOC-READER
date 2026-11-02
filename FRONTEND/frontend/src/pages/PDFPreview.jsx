
import { useNavigate, useParams } from "react-router-dom";

import WorkspaceHeader from "../components/documents/WorkspaceHeader";
import PDFViewer from "../components/documents/PDFViewer";
import AIChatPanel from "../components/documents/AIChatPanel";

import usePDFDocument from "../hooks/usePDFDocument";

export default function PDFPreview() {
  const navigate = useNavigate();
  const { documentId } = useParams();

  const {
    pdfUrl,
    loading,
    error,
  } = usePDFDocument(documentId);

  return (
    <div className="h-screen bg-slate-950 text-white flex flex-col overflow-hidden">

      {/* Top Navigation */}
      <WorkspaceHeader
        onBack={() => navigate("/dashboard")}
        pdfUrl={pdfUrl}
      />

      {/* Main Workspace */}
      <main className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-[60%_40%]">

        {/* Left: PDF Viewer */}
        <PDFViewer
          pdfUrl={pdfUrl}
          loading={loading}
          error={error}
        />

        {/* Right: AI Chat */}
        <AIChatPanel />

      </main>

    </div>
  );
}
