
import {
  FileText,
  Loader2,
} from "lucide-react";

export default function PDFViewer({
  pdfUrl,
  loading,
  error,
}) {
  return (
    <section className="min-h-0 bg-slate-900 border-r border-slate-800 flex flex-col">

      {/* PDF Header */}
      <div className="h-12 shrink-0 px-5 border-b border-slate-800 flex items-center justify-between">

        <div className="flex items-center gap-2">
          <FileText size={17} className="text-blue-400" />

          <h2 className="font-semibold text-sm">
            PDF Preview
          </h2>
        </div>

        <span className="text-xs text-slate-500">
          Document Viewer
        </span>

      </div>

      {/* PDF Content */}
      <div className="flex-1 min-h-0 bg-slate-800">

        {loading && (
          <div className="h-full flex flex-col items-center justify-center gap-3">

            <Loader2
              size={32}
              className="animate-spin text-blue-400"
            />

            <p className="text-slate-400 text-sm">
              Loading your document...
            </p>

          </div>
        )}

        {!loading && error && (
          <div className="h-full flex flex-col items-center justify-center gap-3 p-6">

            <FileText size={40} className="text-red-400" />

            <p className="text-red-400 text-center">
              {error}
            </p>

          </div>
        )}

        {!loading && !error && pdfUrl && (
          <iframe
            src={pdfUrl}
            title="PDF Document Preview"
            className="w-full h-full bg-white"
          />
        )}

      </div>

    </section>
  );
}
