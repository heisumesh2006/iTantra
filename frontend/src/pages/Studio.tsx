import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ArrowRight, Radio, Send, RefreshCw } from "lucide-react";
import { api, baseline, message } from "../api";
import { useAudio } from "../context";
import type {
  Capabilities,
  Channel,
  Job,
  Mode,
  TransmissionConfig,
} from "../types";
import { PageTitle, Panel, ErrorBox, Empty, Busy } from "../components/ui";
import { AudioInput } from "../components/AudioInput";
import { ChannelControls } from "../components/ChannelControls";
import { Results } from "../components/Results";
export default function Studio({ live = false }: { live?: boolean }) {
  const { media, setMedia } = useAudio();
  const [params] = useSearchParams();
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [language, setLanguage] = useState("en");
  const [mode, setMode] = useState<Mode>("conventional");
  const [channel, setChannel] = useState<Channel>({ ...baseline });
  const [bandwidth, setBandwidth] = useState(3);
  const [budget, setBudget] = useState(8);
  const [text, setText] = useState("");
  const [manual, setManual] = useState(false);
  const [reference, setReference] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showChannel, setShowChannel] = useState(true);
  const [history, setHistory] = useState<Job[]>([]);
  const active =
    submitting || job?.status === "running" || job?.status === "queued";
  useEffect(() => {
    void api<Capabilities>("/capabilities")
      .then(setCaps)
      .catch((e) => setError(message(e)));
    const id = params.get("id");
    if (id)
      void api<Job>("/transmissions/" + id)
        .then((j) => {
          setJob(j);
          setLanguage(j.config.language);
          setMode(j.config.mode);
          setChannel(j.config.channel_config);
          if (j.result?.source) setMedia(j.result.source);
        })
        .catch((e) => setError(message(e)));
  }, [params]);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const timer = setInterval(() => {
      void api<Job>("/transmissions/" + job.id)
        .then((j) => {
          setJob(j);
          if (j.status === "completed")
            setHistory((h) =>
              [j, ...h.filter((v) => v.id !== j.id)].slice(0, 8),
            );
        })
        .catch((e) => {
          setError(message(e));
          clearInterval(timer);
        });
    }, 1000);
    return () => clearInterval(timer);
  }, [job?.id, job?.status]);
  async function send() {
    setSubmitting(true);
    setError(null);
    try {
      const config: TransmissionConfig = {
        mode,
        language,
        media_id: media?.id,
        bandwidth_kbps: bandwidth,
        budget_kbps: budget,
        objective: "meaning",
        target_latency_ms: 10000,
        channel_config: channel,
        reference: reference || undefined,
        ...(manual && mode === "semantic" ? { text } : {}),
      };
      setJob(
        await api<Job>("/transmissions", {
          method: "POST",
          body: JSON.stringify(config),
        }),
      );
    } catch (e) {
      setError(message(e));
    } finally {
      setSubmitting(false);
    }
  }
  const selected = caps?.languages.find((l) => l.code === language);
  return (
    <>
      <PageTitle
        tag={
          live ? "TURN-BASED · LOCAL DEMONSTRATION" : "WORKSPACE / TRANSCEIVER"
        }
        title={live ? "Push. Send. Listen" : "Neural Transceiver Studio"}
        description={
          live
            ? "Send each voice turn through the actual encode, simulated radio, and receiver pipeline."
            : "One voice. Three representations. A measurable journey across a simulated radio link."
        }
        action={
          <span className="badge">
            <i />
            SIMULATION MODE
          </span>
        }
      />
      <ErrorBox error={error || job?.error || null} />
      <div className="studio-grid">
        <Panel
          title="Transmitter"
          eyebrow="01 / SOURCE"
          action={<span className="node-indicator">TX</span>}
        >
          <AudioInput />
          <div className="form-section">
            <label>
              Input language
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                {(
                  caps?.languages || [
                    { code: "en", name: "English", native: "English" },
                  ]
                ).map((l) => (
                  <option value={l.code} key={l.code}>
                    {l.name} · {l.native}
                  </option>
                ))}
              </select>
            </label>
            <div className="capability-line">
              <span className={selected?.stt_installed ? "positive" : ""}>
                STT {selected?.stt_installed ? "installed" : "not installed"}
              </span>
              <span className={selected?.tts_installed ? "positive" : ""}>
                TTS {selected?.tts_installed ? "installed" : "not installed"}
              </span>
            </div>
            <label>
              Communication mode
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as Mode)}
              >
                <option value="conventional">A · Conventional / Opus</option>
                <option value="neural">B · Neural / EnCodec</option>
                <option value="semantic">C · Semantic / STT → TTS</option>
                <option value="adaptive">
                  D · Adaptive / explainable rules
                </option>
              </select>
            </label>
            {mode === "neural" && (
              <label>
                Neural target bandwidth
                <select
                  value={bandwidth}
                  onChange={(e) => setBandwidth(+e.target.value)}
                >
                  {[1.5, 3, 6, 12].map((b) => (
                    <option key={b} value={b}>
                      {b} kbps · before metadata
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label>
              Wire budget (kbps per speech second)
              <input
                type="number"
                min={0.1}
                max={256}
                step={0.1}
                value={budget}
                onChange={(e) => setBudget(+e.target.value)}
              />
            </label>
            {mode === "semantic" && (
              <>
                <label className="check">
                  <input
                    type="checkbox"
                    checked={manual}
                    onChange={(e) => setManual(e.target.checked)}
                  />
                  Use explicit text input (bypasses STT)
                </label>
                {manual && (
                  <textarea
                    value={text}
                    maxLength={1000}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Type text in the selected language"
                    aria-label="Manual semantic text"
                  />
                )}
                <label>
                  Reference transcript (optional)
                  <textarea
                    value={reference}
                    maxLength={4000}
                    onChange={(e) => setReference(e.target.value)}
                    placeholder="Human reference for WER / CER"
                  />
                </label>
              </>
            )}
            {job?.result?.sender_text && (
              <div className="transcript">
                <span className="eyebrow">Sender transcription</span>
                <p>{job.result.sender_text}</p>
              </div>
            )}
          </div>
        </Panel>
        <Panel
          title="Radio link"
          eyebrow="02 / SOFTWARE CHANNEL"
          action={<Radio size={20} className="cyan" />}
        >
          <div className={"radio-visual " + (active ? "transmitting" : "")}>
            <div className="radio-node">TX</div>
            <div className="signal-line">
              <i />
              <i />
              <i />
            </div>
            <div className="radio-node">RX</div>
          </div>
          <div className="link-state">
            <strong>{channel.modulation}</strong>
            <span>{channel.channel.toUpperCase()}</span>
            <strong className="cyan">
              {channel.snr_db} <small>dB Es/N0</small>
            </strong>
          </div>
          <p className="muted small">
            Unit symbol energy · coherent detection · strict all-packet recovery
          </p>
          <button
            className="text-link"
            onClick={() => setShowChannel((v) => !v)}
          >
            {showChannel ? "Hide" : "Show"} link parameters
          </button>
          {showChannel && (
            <ChannelControls value={channel} onChange={setChannel} />
          )}
          <button
            className="start-button"
            onClick={() => void send()}
            disabled={
              !!active ||
              (!media && !(mode === "semantic" && manual && text.trim()))
            }
          >
            {active ? (
              <Busy label="Pipeline active" />
            ) : (
              <>
                <Send size={17} />
                {live ? "Send voice turn" : "Start Transmission"}
                <ArrowRight size={17} />
              </>
            )}
          </button>
          {active && job && (
            <button
              className="secondary full"
              onClick={() =>
                void api("/transmissions/" + job.id + "/cancel", {
                  method: "POST",
                }).catch((e) => setError(message(e)))
              }
            >
              Request cancellation
            </button>
          )}
          {job && (
            <div className="stages">
              <span className="eyebrow">BACKEND EVENT LOG</span>
              {job.stages.map((s, i) => (
                <div key={i}>
                  <i
                    className={
                      i === job.stages.length - 1 && active ? "active" : ""
                    }
                  />
                  <span>{s.name}</span>
                </div>
              ))}
              <p className="muted small">
                {job.status} · {job.id.slice(0, 8)}
              </p>
            </div>
          )}
        </Panel>
        <Panel
          title="Receiver"
          eyebrow="03 / RECOVERED INFORMATION"
          action={<span className="node-indicator violet">RX</span>}
        >
          {job?.result ? (
            <Results result={job.result} compact />
          ) : (
            <Empty>
              {active
                ? "Waiting for recovered information. Decoder runs only after valid packet recovery."
                : "Receiver is ready. Start a transmission to inspect reconstructed audio and measured results."}
            </Empty>
          )}
        </Panel>
      </div>
      {job?.result && (
        <Panel
          title="Transmission record"
          eyebrow="REPRODUCIBLE SESSION"
          action={
            <a
              className="text-link"
              href={"/api/v1/exports/transmissions/" + job.id + "?format=json"}
            >
              Export JSON <ArrowRight size={14} />
            </a>
          }
        >
          <div className="record-details">
            <span>
              Seed <b>{job.result.config.channel_config.seed}</b>
            </span>
            <span>
              Codec <b>{job.result.mode}</b>
            </span>
            <span>
              Payload <b>{job.result.metrics.payload_bytes} bytes</b>
            </span>
            <span>
              Wire <b>{job.result.metrics.total_transmitted_bits} bits</b>
            </span>
            <a href={"/studio?id=" + job.id}>
              <RefreshCw size={14} />
              Reopen saved session
            </a>
          </div>
        </Panel>
      )}
      {live && history.length > 0 && (
        <Panel title="This conversation" eyebrow="LOCAL VOICE TURNS">
          {history.map((j) => (
            <div className="conversation" key={j.id}>
              <span>{new Date(j.created_at).toLocaleTimeString()}</span>
              <strong>
                {j.result?.recovered_text || j.result?.recovery_status}
              </strong>
              {j.result?.receiver && (
                <audio controls src={j.result.receiver.url} />
              )}
            </div>
          ))}
        </Panel>
      )}
    </>
  );
}
