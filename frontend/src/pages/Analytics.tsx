
import { useEffect, useState } from "react";
import { api, baseline, message } from "../api";
import { useAudio } from "../context";
import type { Experiment, Metrics } from "../types";
import { PageTitle, Panel, Busy, ErrorBox } from "../components/ui";
export default function Analytics() {
  const { media } = useAudio();
  const [runs, setRuns] = useState<
    (Metrics & { mode: string; language: string; id: string })[]
  >([]);
  const [job, setJob] = useState<Experiment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState("en");
  const [reference, setReference] = useState("");
  const [snrs, setSnrs] = useState("4,8,12");
  const [repeats, setRepeats] = useState(1);
  const [busy, setBusy] = useState(false);
  async function refresh() {
    try {
      const data = await api<{ runs: typeof runs }>("/metrics/summary");
      setRuns(data.runs);
    } catch (e) {
      setError(message(e));
    }
  }
  useEffect(() => {
    void refresh();
  }, []);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const timer = setInterval(() => {
      void api<Experiment>("/experiments/" + job.id)
        .then((j) => {
          setJob(j);
          if (j.status === "completed") void refresh();
        })
        .catch((e) => {
          setError(message(e));
          clearInterval(timer);
        });
    }, 1500);
    return () => clearInterval(timer);
  }, [job?.id, job?.status]);
  async function run() {
    if (!media) return;
    setBusy(true);
    setError(null);
    try {
      setJob(
        await api<Experiment>("/experiments/run", {
          method: "POST",
          body: JSON.stringify({
            media_id: media.id,
            language,
            reference: reference || null,
            modes: ["conventional", "neural", "semantic"],
            snr_values: snrs.split(",").map(Number),
            repeats,
            config: baseline,
          }),
        }),
      );
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <><PageTitle
        tag="RESEARCH / MEASURED OUTCOMES"
        title="Performance Analytics"
        description="Trace every comparison to a saved source, channel configuration, model and seed."
      /><ErrorBox error={error || job?.error || null} /><Panel
        title="Run a controlled mode comparison"
        eyebrow="SAME SOURCE / CONFIGURATION"
      >
        <div className="experiment-form">
          <label>
            Language
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {["en", "hi", "kn", "ta", "te", "ml"].map((l) => (
                <option key={l}>{l}</option>
              ))}
            </select>
          </label>
          <label>
            Es/N0 points (comma separated)
            <input value={snrs} onChange={(e) => setSnrs(e.target.value)} />
          </label>
          <label>
            Repeats / independent seeds
            <input
              type="number"
              min={1}
              max={5}
              value={repeats}
              onChange={(e) => setRepeats(+e.target.value)}
            />
          </label>
          <label>
            Reference transcript
            <input
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              placeholder="Optional human transcript"
            />
          </label>
          <button
            onClick={() => void run()}
            disabled={
              !media ||
              busy ||
              job?.status === "running" ||
              job?.status === "queued"
            }
          >
            {busy || job?.status === "running" || job?.status === "queued" ? (
              <Busy label="Experiment running" />
            ) : (
              "Run A / B / C"
            )}
          </button>
        </div>
        <p className="muted small">
          {media
            ? `Current source: ${media.duration_seconds.toFixed(2)} seconds`
            : "Upload a source in the Transceiver Studio first."}{" "}
          · Default AWGN, BPSK, packet payload 256 bytes. Missing models are
          recorded as unavailable.
        </p>
        {job && (
          <div className="button-row">
            <span className="badge">
              {job.status} · {job.id.slice(0, 8)}
            </span>
            <a
              className="text-link"
              href={"/api/v1/exports/experiments/" + job.id + "?format=json"}
            >
              JSON
            </a>
            <a
              className="text-link"
              href={"/api/v1/exports/experiments/" + job.id + "?format=csv"}
            >
              CSV
            </a>
            {["queued", "running"].includes(job.status) && (
              <button
                className="text-link"
                onClick={() =>
                  void api("/experiments/" + job.id + "/cancel", {
                    method: "POST",
                  })
                }
              >
                Cancel
              </button>
            )}
          </div>
        )}
      </Panel></>
  );
}