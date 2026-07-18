import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";
import {
  BrainCircuit,
  MessageSquare,
  FileSearch,
  BookMarked,
  Database,
  Zap,
  History,
  ArrowRight,
} from "lucide-react";

/* ─── Animation Variants ──────────────────── */
const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number] },
  }),
};

const stagger = {
  visible: { transition: { staggerChildren: 0.06 } },
};

/* ─── Feature Data ────────────────────────── */
const FEATURES = [
  {
    icon: MessageSquare,
    title: "Smart PDF Chat",
    desc: "Ask natural language questions about your uploaded research papers and get precise answers.",
  },
  {
    icon: History,
    title: "Conversation Memory",
    desc: "Context-aware dialogue that remembers previous questions within the same session.",
  },
  {
    icon: FileSearch,
    title: "Semantic Search",
    desc: "Vector-based retrieval finds the most relevant passages, not just keyword matches.",
  },
  {
    icon: BookMarked,
    title: "Source Citations",
    desc: "Every answer includes the exact documents and page numbers used to generate it.",
  },
  {
    icon: Database,
    title: "Persistent Knowledge Base",
    desc: "Uploaded documents are chunked, embedded, and stored for instant future retrieval.",
  },
  {
    icon: Zap,
    title: "Fast Retrieval",
    desc: "ChromaDB vector store enables sub-second similarity search across all your papers.",
  },
];

/* ─── Architecture Steps ──────────────────── */
const PIPELINE = [
  { label: "PDFs", sub: "Upload" },
  { label: "Chunking", sub: "Split" },
  { label: "Embeddings", sub: "Vectorize" },
  { label: "Vector DB", sub: "Store" },
  { label: "LLM", sub: "Generate" },
  { label: "Response", sub: "Cite" },
];

/* ─── Tech Stack ──────────────────────────── */
const TECH = [
  "React", "TypeScript", "Tailwind CSS", "FastAPI",
  "LangChain", "ChromaDB", "SQLite", "Gemini",
];

/* ─── Component ───────────────────────────── */
export default function Landing() {
  const navigate = useNavigate();
  const { login, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, navigate]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-bg">
        <span className="w-1.5 h-1.5 rounded-full bg-accent animate-ping" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="min-h-screen bg-bg"
    >
      {/* ── Nav ──────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-border/50 bg-bg/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-14">
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-accent-subtle">
              <BrainCircuit size={15} className="text-accent" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-text-primary">
              ResearchMind
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium
                         bg-accent text-white hover:bg-accent-hover transition-colors cursor-pointer"
            >
              Dashboard
              <ArrowRight size={12} />
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────── */}
      <section className="relative overflow-hidden pt-14">
        {/* Animated background orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="orb-1 absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-accent/[0.04] blur-[120px]" />
          <div className="orb-2 absolute top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-violet/[0.05] blur-[100px]" />
          <div className="orb-3 absolute bottom-1/4 left-1/2 w-[350px] h-[350px] rounded-full bg-accent/[0.03] blur-[80px]" />
        </div>
        <div className="grid-bg absolute inset-0 pointer-events-none" />

        <div className="relative max-w-4xl mx-auto px-6 pt-28 pb-24 text-center">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
          >
            {/* Badge */}
            <motion.div variants={fadeUp} custom={0} className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-surface-elevated/50 mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              <span className="text-xs text-text-secondary">Open-source research assistant</span>
            </motion.div>

            {/* Title */}
            <motion.h1 variants={fadeUp} custom={1} className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
              <span className="gradient-text">AI Research</span>
              <br />
              <span className="text-text-primary">Assistant</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p variants={fadeUp} custom={2} className="max-w-2xl mx-auto text-base sm:text-lg text-text-secondary leading-relaxed mb-10">
              A modern AI-powered research workspace for exploring papers,
              asking questions, retrieving citations, and organizing knowledge.
            </motion.p>

            {/* Buttons */}
            <motion.div variants={fadeUp} custom={3} className="flex items-center justify-center gap-3">
              {!isAuthenticated ? (
                <div className="shadow-lg hover:shadow-xl transition-all rounded-lg overflow-hidden">
                  <GoogleLogin
                    onSuccess={(credentialResponse) => {
                      if (credentialResponse.credential) {
                        login(credentialResponse.credential);
                      }
                    }}
                    onError={() => {
                      console.log("Login Failed");
                    }}
                    theme="outline"
                    shape="pill"
                  />
                </div>
              ) : (
                <button
                  onClick={() => navigate("/dashboard")}
                  className="group flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium
                             bg-accent text-white hover:bg-accent-hover transition-all cursor-pointer
                             shadow-[0_0_20px_rgba(99,102,241,0.15)]
                             hover:shadow-[0_0_30px_rgba(99,102,241,0.25)]"
                >
                  Go to Dashboard
                  <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
                </button>
              )}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Features ─────────────────────────── */}
      <section className="relative max-w-5xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
        >
          <motion.p variants={fadeUp} custom={0} className="text-xs font-medium text-accent uppercase tracking-widest mb-2">
            Features
          </motion.p>
          <motion.h2 variants={fadeUp} custom={1} className="text-2xl sm:text-3xl font-bold text-text-primary mb-12">
            Everything you need for
            <br />
            <span className="text-text-secondary">AI-powered research</span>
          </motion.h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-border/50 rounded-xl overflow-hidden border border-border/50">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i + 2}
                className="group bg-bg p-6 hover:bg-surface-elevated/30 transition-colors"
              >
                <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-surface-elevated group-hover:bg-accent-subtle transition-colors mb-4">
                  <f.icon size={17} className="text-text-muted group-hover:text-accent transition-colors" />
                </div>
                <h3 className="text-sm font-semibold text-text-primary mb-1.5">{f.title}</h3>
                <p className="text-xs text-text-muted leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Architecture ─────────────────────── */}
      <section className="relative max-w-5xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
        >
          <motion.p variants={fadeUp} custom={0} className="text-xs font-medium text-accent uppercase tracking-widest mb-2">
            Architecture
          </motion.p>
          <motion.h2 variants={fadeUp} custom={1} className="text-2xl sm:text-3xl font-bold text-text-primary mb-12">
            How it works
          </motion.h2>

          {/* Pipeline */}
          <motion.div variants={fadeUp} custom={2} className="flex items-center justify-between gap-4 overflow-x-auto pb-4 max-w-3xl mx-auto">
            {PIPELINE.map((step, i) => (
              <div key={step.label} className="flex items-center gap-4 shrink-0">
                <div className="flex flex-col items-center text-center">
                  <span className="text-sm font-semibold text-text-primary">{step.label}</span>
                  <span className="text-[10px] text-text-muted mt-1">{step.sub}</span>
                </div>
                {i < PIPELINE.length - 1 && (
                  <div className="flex items-center justify-center text-text-muted shrink-0">
                    <ArrowRight size={14} className="text-accent animate-pulse" />
                  </div>
                )}
              </div>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* ── Tech Stack ───────────────────────── */}
      <section className="relative max-w-5xl mx-auto px-6 py-24">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={stagger}
        >
          <motion.p variants={fadeUp} custom={0} className="text-xs font-medium text-accent uppercase tracking-widest mb-2">
            Tech Stack
          </motion.p>
          <motion.h2 variants={fadeUp} custom={1} className="text-2xl sm:text-3xl font-bold text-text-primary mb-8">
            Built with modern tools
          </motion.h2>

          <motion.div variants={fadeUp} custom={2} className="flex flex-wrap gap-2">
            {TECH.map((t) => (
              <span
                key={t}
                className="inline-flex items-center px-3.5 py-1.5 rounded-lg border border-border
                           bg-surface-elevated/50 text-xs font-medium text-text-secondary
                           hover:text-text-primary hover:border-border-strong transition-colors"
              >
                {t}
              </span>
            ))}
          </motion.div>
        </motion.div>
      </section>

      {/* ── Footer ───────────────────────────── */}
      <footer className="border-t border-border">
        <div className="max-w-5xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <BrainCircuit size={14} className="text-text-muted" />
            <span className="text-xs text-text-muted">
              ResearchMind — AI Research Assistant
            </span>
            <span className="text-[10px] text-text-faint px-1.5 py-0.5 rounded bg-surface-elevated">
              v1.0
            </span>
          </div>
          <div>
            <span className="text-xs text-text-muted">
              created by mohit nirmal @ 2026
            </span>
          </div>
        </div>
      </footer>
    </motion.div>
  );
}
