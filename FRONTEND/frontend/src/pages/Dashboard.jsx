
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpen,
  FileText,
  MessageSquareText,
  Plus,
  Search,
  Sparkles,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "../store/authStore";

export default function Dashboard() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);

    try {
      await logout();
    } finally {
      navigate("/login", { replace: true });
    }
  }

  const displayName = user?.name || user?.full_name || "Learner";

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <a className="brand" href="/dashboard">
          <span className="brand-icon">K</span>
          Knowledge Hub
        </a>

        <p className="nav-label">WORKSPACE</p>

        <a className="nav-item active" href="/dashboard">
          <BookOpen size={18} /> Overview
        </a>
        <button
          className="nav-item"
          onClick={() => alert("Document management is coming next.")}
        >
          <FileText size={18} /> My Documents
        </button>
        <button
          className="nav-item"
          onClick={() => alert("RAG chat is coming next.")}
        >
          <MessageSquareText size={18} /> AI Chat
        </button>

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

      <main className="dashboard-main">
        <header className="topbar">
          <div>
            <span className="muted">Workspace / Overview</span>
          </div>
          <span className="status-pill">
            <span className="status-dot" /> Authenticated
          </span>
        </header>

        <section className="welcome-section">
          <div>
            <p className="eyebrow">YOUR PERSONAL KNOWLEDGE SPACE</p>
            <h1>Good to see you, {displayName}.</h1>
            <p className="muted">
              Bring your knowledge together and let AI help you explore it.
            </p>
          </div>
          <div className="welcome-icon">
            <Sparkles size={34} />
          </div>
        </section>

        <section className="stats-grid">
          <article className="stat-card">
            <div className="stat-icon purple"><FileText /></div>
            <p className="muted">Documents</p>
            <h2>0</h2>
            <span>Ready to organize</span>
          </article>

          <article className="stat-card">
            <div className="stat-icon blue"><MessageSquareText /></div>
            <p className="muted">AI conversations</p>
            <h2>0</h2>
            <span>Your future AI workspace</span>
          </article>

          <article className="stat-card">
            <div className="stat-icon orange"><BookOpen /></div>
            <p className="muted">Knowledge bases</p>
            <h2>0</h2>
            <span>Build your first collection</span>
          </article>
        </section>

        <section className="content-card">
          <div className="section-heading">
            <div>
              <h2>Get started</h2>
              <p className="muted">
                Your next step toward a personal AI research assistant.
              </p>
            </div>
            <Sparkles size={22} />
          </div>

          <div className="empty-state">
            <div className="empty-icon"><FileText size={28} /></div>
            <h3>Your knowledge hub starts here</h3>
            <p className="muted">
              Upload PDFs and notes, then ask questions using retrieval-
              augmented generation (RAG).
            </p>
            <button
              className="primary-btn compact-btn"
              onClick={() => alert("We'll implement document upload next.")}
            >
              <Plus size={18} /> Add your first document
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}
