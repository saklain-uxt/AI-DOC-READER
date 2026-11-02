
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  BookOpen,
  FileText,
  MessageSquareText,
  Sparkles,
  LogOut,
  UploadCloud,
} from "lucide-react";

import { useAuthStore } from "../store/authStore";
import { useDocumentStore } from "../store/documentStore";

import UploadArea from "../components/documents/UploadArea";
import DocumentList from "../components/documents/DocumentList";

export default function Dashboard() {
  const navigate = useNavigate();

  // Authentication state
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  // Document state
  const documents = useDocumentStore(
    (state) => state.documents
  );

  const fetchDocuments = useDocumentStore(
    (state) => state.fetchDocuments
  );

  // Local component state
  const [loggingOut, setLoggingOut] = useState(false);

  // Fetch documents when Dashboard loads.
  // DocumentList also fetches on mount, so we use that
  // component as the single source for initial fetching.

  // Display user's name.
  const displayName =
    user?.name || user?.full_name || "Learner";

  // Handle logout.
  async function handleLogout() {
    setLoggingOut(true);

    try {
      await logout();
    } finally {
      navigate("/login", { replace: true });
    }
  }

  // Scroll to document upload section.
  function scrollToUpload() {
    document.getElementById("upload-section")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  // Scroll to document list.
  function scrollToDocuments() {
    document.getElementById("my-documents")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <div className="dashboard-layout">

      {/* Sidebar */}
      <aside className="sidebar">

        <a className="brand" href="/dashboard">
          <span className="brand-icon">K</span>
          Knowledge Hub
        </a>

        <p className="nav-label">WORKSPACE</p>

        <a className="nav-item active" href="/dashboard">
          <BookOpen size={18} />
          Overview
        </a>

        <button
          className="nav-item"
          type="button"
          onClick={scrollToDocuments}
        >
          <FileText size={18} />
          My Documents
        </button>

        <button
          className="nav-item"
          type="button"
          onClick={() => alert("AI Chat is coming next.")}
        >
          <MessageSquareText size={18} />
          AI Chat
        </button>

        {/* Sidebar user information */}
        <div className="sidebar-bottom">

          <div className="avatar">
            {displayName.charAt(0).toUpperCase()}
          </div>

          <div className="user-info">
            <strong>{displayName}</strong>
            <span>{user?.email || "Signed in"}</span>
          </div>

          <button
            className="icon-btn"
            onClick={handleLogout}
            disabled={loggingOut}
            title="Log out"
            aria-label="Log out"
          >
            <LogOut size={18} />
          </button>

        </div>
      </aside>

      {/* Main Dashboard */}
      <main className="dashboard-main">

        {/* Topbar */}
        <header className="topbar">
          <div>
            <span className="muted">
              Workspace / Overview
            </span>
          </div>

          <span className="status-pill">
            <span className="status-dot" />
            Authenticated
          </span>
        </header>

        {/* Welcome Section */}
        <section className="welcome-section">

          <div>
            <p className="eyebrow">
              YOUR PERSONAL KNOWLEDGE SPACE
            </p>

            <h1>
              Good to see you, {displayName}.
            </h1>

            <p className="muted">
              Bring your knowledge together and let AI help
              you explore it.
            </p>
          </div>

          <div className="welcome-icon">
            <Sparkles size={34} />
          </div>

        </section>

        {/* Statistics */}
        <section className="stats-grid">

          {/* Document count */}
          <article className="stat-card">
            <div className="stat-icon purple">
              <FileText />
            </div>

            <p className="muted">Documents</p>

            <h2>{documents.length}</h2>

            <span>Uploaded documents</span>
          </article>

          {/* AI conversations */}
          <article className="stat-card">
            <div className="stat-icon blue">
              <MessageSquareText />
            </div>

            <p className="muted">AI conversations</p>

            <h2>0</h2>

            <span>Your AI workspace</span>
          </article>

          {/* Knowledge bases */}
          <article className="stat-card">
            <div className="stat-icon orange">
              <BookOpen />
            </div>

            <p className="muted">Knowledge bases</p>

            <h2>0</h2>

            <span>Build your first collection</span>
          </article>

        </section>

        {/* Upload Document Section */}
        <div id="upload-section">
          <UploadArea />
        </div>

        {/* Document List Section */}
        <div id="my-documents">
          <DocumentList />
        </div>

      </main>
    </div>
  );
}
