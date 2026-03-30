
import { useEffect, useState } from "react";
import { api, baseline, message } from "../api";
import { useAudio } from "../context";
import type { Experiment, Capabilities } from "../types";
import { PageTitle, Panel, Busy, ErrorBox } from "../components/ui";
import { AudioInput, Spectrogram } from "../components/AudioInput";
export default function Compression() {
  const { media } = useAudio();
  const [job, setJob] = useState<Experiment | null>(null);
  const [caps, setCaps] = useState<Capabilities | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    void api<Capabilities>("/capabilities")
      .then(setCaps)
      .catch((e) => setError(message(e)));
  }, []);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) return;
    const timer = setInterval(() => {
      void api<Experiment>("/experiments/" + job.id)
        .then(setJob)
        .catch((e) => {
          setError(message(e));
          clearInterval(timer);
        });
    }, 1200);
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
            language: "en",
            modes: ["conventional", "neural"],
            snr_values: [30],
            repeats: 1,
            config: { ...baseline, channel: "ideal" },
          }),
        }),
      );
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  const active = busy || job?.status === "running" || job?.status === "queued";
  return (
    <><PageTitle
        tag="CODECS / SAME SOURCE COMPARISON"
        title="Compression Comparison"
        description="Compare actual Opus and EnCodec bitstreams through an ideal channel using the same recording."
      /><ErrorBox error={error || job?.error || null} /><div className="two-col"><Panel title="Shared source" eyebrow="CONTROLLED AUDIO">
          <AudioInput />
          {media && <Spectrogram media={media} />}
        </Panel><Panel title="Comparison protocol" eyebrow="HONEST RATE ACCOUNTING">
          <p>
            Opus: 12 kbps target, mono, 20 ms frames. Neural: EnCodec 24 kHz at
            3 kbps, with real 10-bit codebook indices.
          </p>
          <p>
            Includes Ogg or neural metadata, every packet header, CRC and coding
            overhead. SI-SDR uses the common resampled waveform and is not a
            perceptual score.
          </p>
          <div className="note">
            EnCodec {caps?.neural.installed ? "installed" : "not installed"} ·{" "}
            {caps?.neural.verified ? "round trip verified" : "not yet verified"}
          </div>
          <button disabled={!media || !!active} onClick={() => void run()}>
            {active ? (
              <Busy label="Comparing real codecs" />
            ) : (
              "Compare both codecs"
            )}
          </button>
          {job && (
            <a
              className="text-link"
              href={"/api/v1/exports/experiments/" + job.id + "?format=csv"}
            >
              Export CSV
            </a>
          )}
        </Panel></div></>
  );
}