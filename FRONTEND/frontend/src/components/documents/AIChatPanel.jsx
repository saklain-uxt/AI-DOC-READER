
import { useState } from "react";

import {
  Bot,
  Sparkles,
  MessageCircle,
  Send,
} from "lucide-react";

export default function AIChatPanel() {
  const [message, setMessage] = useState("");

  const suggestedQuestions = [
    "Summarize this document",
    "What are the key points?",
    "Explain this document in simple words",
    "Find important information",
  ];

  return (
    <section className="min-h-0 bg-slate-950 flex flex-col">

      {/* Chat Header */}
      <div className="h-16 shrink-0 px-5 border-b border-slate-800 flex items-center gap-3">

        <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center">
          <Bot size={23} className="text-blue-400" />
        </div>

        <div>
          <h2 className="font-semibold text-sm">
            AI Assistant
          </h2>

          <p className="text-xs text-slate-500">
            Your document assistant
          </p>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />

          <span className="text-xs text-slate-400">
            Ready
          </span>
        </div>

      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-5">

        <div className="min-h-full flex flex-col items-center justify-center text-center">

          <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-5">
            <Sparkles size={32} className="text-blue-400" />
          </div>

          <h3 className="text-xl font-semibold mb-2">
            Chat with your PDF
          </h3>

          <p className="text-sm text-slate-400 max-w-sm leading-relaxed">
            Ask questions, summarize content, extract
            important information and understand
            complex topics from your document.
          </p>

          {/* Suggested Questions */}
          <div className="mt-8 w-full space-y-3">

            <p className="text-xs text-slate-500 text-left">
              SUGGESTED QUESTIONS
            </p>

            {suggestedQuestions.map((question) => (
              <button
                key={question}
                type="button"
                disabled
                className="w-full flex items-center gap-3 text-left text-sm p-3 rounded-xl border border-slate-800 bg-slate-900/50 text-slate-400 opacity-60 cursor-not-allowed"
              >
                <MessageCircle
                  size={16}
                  className="text-blue-400 shrink-0"
                />

                {question}
              </button>
            ))}

          </div>

        </div>

      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-slate-800">

        <div className="bg-slate-900 border border-slate-700 rounded-xl p-3">

          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask anything about this PDF..."
            rows={2}
            disabled
            className="w-full bg-transparent outline-none resize-none text-sm text-white placeholder:text-slate-500"
          />

          <div className="flex justify-between items-center mt-2">

            <span className="text-xs text-slate-500">
              AI chat coming soon
            </span>

            <button
              type="button"
              disabled
              className="p-2 rounded-lg bg-blue-600/40 text-white/50 cursor-not-allowed"
            >
              <Send size={18} />
            </button>

          </div>

        </div>

        <p className="text-xs text-slate-600 text-center mt-3">
          AI responses will be based on your uploaded document.
        </p>

      </div>

    </section>
  );
}
