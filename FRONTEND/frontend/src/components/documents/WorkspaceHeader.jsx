
import {
  ArrowLeft,
  Download,
  FileText,
} from "lucide-react";

export default function WorkspaceHeader({
  onBack,
  pdfUrl,
}) {
  return (
    <header className="h-16 shrink-0 border-b border-slate-800 px-5 flex items-center justify-between">

      <button
        onClick={onBack}
        className="flex items-center gap-2 text-slate-300 hover:text-white transition"
      >
        <ArrowLeft size={20} />
        <span className="hidden sm:inline">
          Back to Documents
        </span>
      </button>

      <div className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-lg bg-blue-600/20 flex items-center justify-center">
          <FileText size={20} className="text-blue-400" />
        </div>

        <div>
          <h1 className="font-semibold text-sm sm:text-base">
            AI Knowledge Hub
          </h1>

          <p className="text-xs text-slate-500">
            Document Workspace
          </p>
        </div>
      </div>

      {pdfUrl ? (
        <a
          href={pdfUrl}
          download="document.pdf"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-3 py-2 rounded-lg text-sm transition"
        >
          <Download size={17} />
          <span className="hidden sm:inline">
            Download
          </span>
        </a>
      ) : (
        <div className="w-10" />
      )}

    </header>
  );
}
