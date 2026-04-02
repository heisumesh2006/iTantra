
import { useEffect, useState } from "react";
import { api, message } from "../api";
import type { Capabilities } from "../types";
import { PageTitle, ErrorBox } from "../components/ui";
export default function SpeechLab() {
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [language, setLanguage] = useState("en");
  const [tab, setTab] = useState("roundtrip");
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    void api<Capabilities>("/capabilities")
      .then(setCaps)
      .catch((e) => setError(message(e)));
  }, []);
  return (
    <><PageTitle
        tag="SPEECH / LOCAL INFERENCE"
        title="Multilingual Speech Lab"
        description="Inspect real recognition and synthesis, native scripts, model identity and processing time."
      /><div className="language-cards">
        {caps?.languages.map((l) => (
          <button
            className={
              "language-card " + (l.code === language ? "selected" : "")
            }
            key={l.code}
            onClick={() => setLanguage(l.code)}
          >
            <strong lang={l.code}>{l.native}</strong>
            <span>{l.name}</span>
            <small>{l.status}</small>
          </button>
        ))}
      </div><p className="muted small">
        Language statuses reflect installed checkpoints and executed synthetic
        smoke tests. Human-speech quality is not benchmarked. Inspect every
        recognized transcript; recognition errors can propagate.
      </p><div className="tabs">
        {[
          ["stt", "Speech to text"],
          ["tts", "Text to speech"],
          ["roundtrip", "Speech round trip"],
        ].map(([id, label]) => (
          <button
            key={id}
            className={tab === id ? "selected" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div><ErrorBox error={error} /></>
  );
}