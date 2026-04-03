import { useEffect, useState } from "react";
import { Languages, Volume2 } from "lucide-react";
import { api, message } from "../api";
import type { Capabilities, Media } from "../types";
import { useAudio } from "../context";
import { PageTitle, Panel, Busy, ErrorBox, Empty } from "../components/ui";
import { AudioInput, Waveform } from "../components/AudioInput";
export default function SpeechLab() {
  const { media } = useAudio();
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [language, setLanguage] = useState("en");
  const [tab, setTab] = useState("roundtrip");
  const [text, setText] = useState("");
  const [output, setOutput] = useState<Media | null>(null);
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    void api<Capabilities>("/capabilities")
      .then(setCaps)
      .catch((e) => setError(message(e)));
  }, []);
  async function run() {
    setBusy(true);
    setError(null);
    setOutput(null);
    try {
      let transcript = text;
      let detail = "";
      if (tab !== "tts") {
        if (!media) throw new Error("Record or upload audio first.");
        const stt = await api<{
          text: string;
          model: string;
          processing_ms: number;
        }>("/speech/transcribe", {
          method: "POST",
          body: JSON.stringify({ media_id: media.id, language }),
        });
        setText(stt.text);
        transcript = stt.text;
        detail = `STT: ${stt.model} · ${stt.processing_ms.toFixed(1)} ms`;
      }
      if (tab !== "stt") {
        const tts = await api<{
          media: Media;
          model: string;
          processing_ms: number;
        }>("/speech/synthesize", {
          method: "POST",
          body: JSON.stringify({ text: transcript, language }),
        });
        setOutput(tts.media);
        detail += ` · TTS: ${tts.model} · ${tts.processing_ms.toFixed(1)} ms`;
      }
      setInfo(detail);
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageTitle
        tag="SPEECH / LOCAL INFERENCE"
        title="Multilingual Speech Lab"
        description="Inspect real recognition and synthesis, native scripts, model identity and processing time."
      />
      <div className="language-cards">
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
      </div>
      <p className="muted small">
        Language statuses reflect installed checkpoints and executed synthetic
        smoke tests. Human-speech quality is not benchmarked. Inspect every
        recognized transcript; recognition errors can propagate.
      </p>
      <div className="tabs">
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
      </div>
      <ErrorBox error={error} />
      <div className="two-col">
        <Panel title="Speech input" eyebrow="SOURCE">
          {tab !== "tts" && <AudioInput />}
          <label>
            {tab === "tts" ? "Text to synthesize" : "Recognized text"}
            <textarea
              value={text}
              maxLength={1000}
              lang={language}
              onChange={(e) => setText(e.target.value)}
              placeholder="Native script is supported by the installed language model."
            />
          </label>
          <button
            onClick={() => void run()}
            disabled={
              busy ||
              (!media && tab !== "tts") ||
              (!text.trim() && tab === "tts")
            }
          >
            {busy ? (
              <Busy label="Running local inference" />
            ) : (
              <>
                <Languages size={16} />
                Run{" "}
                {tab === "stt"
                  ? "recognition"
                  : tab === "tts"
                    ? "synthesis"
                    : "speech round trip"}
              </>
            )}
          </button>
          <p className="muted small">
            MMS and EnCodec model weights are for noncommercial research
            (CC-BY-NC-4.0). Model downloads are explicit; speech stays local.
          </p>
        </Panel>
        <Panel
          title="Speech output"
          eyebrow="REAL MODEL RESPONSE"
          action={<Volume2 size={18} />}
        >
          {output ? (
            <>
              <Waveform data={output.waveform} />
              <audio controls src={output.url} />
              <a className="text-link" href={output.url} download>
                Download generated audio
              </a>
            </>
          ) : (
            <Empty>
              {busy
                ? "Model inference is running on CPU."
                : "Run a speech task to hear generated audio or inspect the transcript."}
            </Empty>
          )}
          {text && tab !== "tts" && (
            <div className="transcript">
              <span className="eyebrow">Transcript</span>
              <p lang={language}>{text}</p>
            </div>
          )}
          <p className="muted small">
            {info ||
              "Confidence: unavailable. No emotion or speaker identity preservation."}
          </p>
        </Panel>
      </div>
    </>
  );
}
