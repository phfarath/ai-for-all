import { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";

interface HealthState {
  app?: string;
  status?: string;
  environment?: string;
  supabase_configured?: boolean;
  error?: string;
}

const sections = [
  {
    title: "Client",
    description: "React PWA with core navigation and offline-ready architecture."
  },
  {
    title: "API",
    description: "FastAPI v1 gateway exposing modular LMS, CMS, LLM, and analytics routes."
  },
  {
    title: "BaaS",
    description: "Supabase auth, database, and storage for low-cost operations."
  }
];

function HomePage() {
  const [health, setHealth] = useState<HealthState>({});

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .catch((error) => setHealth({ error: error.message }));
  }, []);

  return (
    <main style={{ padding: "4rem 2rem", maxWidth: 960, margin: "0 auto" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <p style={{ color: "#38bdf8", letterSpacing: "0.1em" }}>AI LEARNING PLATFORM</p>
        <h1 style={{ fontSize: "2.5rem", margin: "0.5rem 0" }}>
          Plataforma de ensino de IA
        </h1>
        <p style={{ color: "#cbd5f5" }}>
          Uma arquitetura moderna combinando FastAPI, React PWA e Supabase para experiências de aprendizado personalizadas.
        </p>
      </header>

      <section style={{ display: "grid", gap: "1.5rem" }}>
        {sections.map((section) => (
          <article
            key={section.title}
            style={{
              background: "rgba(15, 23, 42, 0.8)",
              borderRadius: "16px",
              padding: "1.5rem",
              border: "1px solid rgba(94, 234, 212, 0.1)"
            }}
          >
            <h2 style={{ marginTop: 0 }}>{section.title}</h2>
            <p style={{ margin: 0, color: "#e2e8f0" }}>{section.description}</p>
          </article>
        ))}
      </section>

      <section style={{ marginTop: "3rem" }}>
        <h3>Status de Integração</h3>
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            borderRadius: "12px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(148, 163, 184, 0.2)"
          }}
        >
          {health.error ? (
            <p style={{ color: "#fca5a5" }}>Erro ao consultar API: {health.error}</p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              <li>
                <strong>API:</strong> {health.status === "ok" ? "Online" : "Offline"}
              </li>
              <li>
                <strong>Ambiente:</strong> {health.environment ?? "Desconhecido"}
              </li>
              <li>
                <strong>Supabase:</strong> {health.supabase_configured ? "Configurado" : "Não configurado"}
              </li>
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}

export default HomePage;
