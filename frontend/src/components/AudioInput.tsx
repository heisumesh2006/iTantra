import { useEffect, useRef, useState } from "react";
import { Mic, Upload, Square, Pause, Play } from "lucide-react";
import { api, message } from "../api";
import { useAudio } from "../context";
import type { Media } from "../types";
import { Busy, ErrorBox } from "./ui";
export function Waveform({ data }: { data: number[] }) {
  return (
    <div className="waveform" aria-label="Measured waveform envelope">
      {data.map((peak, i) => (
        <i key={i} style={{ height: Math.max(3, peak * 86) + "%" }} />
      ))}
    </div>
  );
}
export function Spectrogram({ media }: { media: Media }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const values = media.spectrogram.values;
    canvas.width = values[0]?.length || 1;
    canvas.height = values.length;
    for (let y = 0; y < values.length; y++)
      for (let x = 0; x < values[y].length; x++) {
        const level = Math.max(0, Math.min(1, (values[y][x] + 100) / 100));
        ctx.fillStyle = `hsl(${250 - level * 90} 65% ${8 + level * 62}%)`;
        ctx.fillRect(x, values.length - 1 - y, 1, 1);
      }
  }, [media]);
  return (
    <figure className="spectrogram">
      <canvas ref={ref} />
      <figcaption>
        Measured STFT · 0–{media.sample_rate / 2} Hz · time →
      </figcaption>
    </figure>
  );
}
export function AudioInput() {
  const { media, setMedia } = useAudio();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<"idle" | "recording" | "paused">("idle");
  const [seconds, setSeconds] = useState(0);
  const recorder = useRef<MediaRecorder | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const chunks = useRef<Blob[]>([]);
  const input = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (state !== "recording") return;
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, [state]);
  useEffect(() => {
    if (seconds >= 60 && recorder.current?.state === "recording")
      recorder.current.stop();
  }, [seconds]);
  useEffect(
    () => () => {
      if (recorder.current && recorder.current.state !== "inactive") {
        recorder.current.onstop = null;
        recorder.current.stop();
      }
      stream.current?.getTracks().forEach((t) => t.stop());
    },
    [],
  );
  async function upload(file: File) {
    setBusy(true);
    setError(null);
    try {
      if (file.size > 15 * 1024 * 1024)
        throw new Error("Maximum upload size is 15 MB.");
      const form = new FormData();
      form.append("file", file);
      setMedia(await api<Media>("/audio", { method: "POST", body: form }));
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  async function record() {
    setError(null);
    try {
      if (!navigator.mediaDevices?.getUserMedia)
        throw new Error(
          "Microphone needs localhost or HTTPS and a supported browser.",
        );
      stream.current = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/ogg";
      recorder.current = new MediaRecorder(stream.current, { mimeType: mime });
      chunks.current = [];
      recorder.current.ondataavailable = (e) => {
        if (e.data.size) chunks.current.push(e.data);
      };
      recorder.current.onstop = () => {
        stream.current?.getTracks().forEach((t) => t.stop());
        setState("idle");
        void upload(
          new File(
            chunks.current,
            "recording." + (mime.includes("webm") ? "webm" : "ogg"),
            { type: mime },
          ),
        );
      };
      recorder.current.start(200);
      setSeconds(0);
      setState("recording");
    } catch (e) {
      stream.current?.getTracks().forEach((t) => t.stop());
      setError(message(e));
    }
  }
  function pause() {
    if (!recorder.current) return;
    if (state === "recording") {
      recorder.current.pause();
      setState("paused");
    } else {
      recorder.current.resume();
      setState("recording");
    }
  }
  return (
    <div>
      <div className="capture-zone">
        <div
          className={
            "capture-icon " + (state === "recording" ? "recording" : "")
          }
        >
          <Mic size={27} />
        </div>
        <strong>
          {state === "idle"
            ? "Bring your voice into the lab"
            : `${state === "paused" ? "Paused" : "Recording"} · ${seconds}s`}
        </strong>
        <p>Local processing · up to 60 seconds · 15 MB</p>
        <div className="button-row">
          {state === "idle" ? (
            <button onClick={() => void record()} disabled={busy}>
              <Mic size={15} />
              Record voice
            </button>
          ) : (
            <>
              <button onClick={() => recorder.current?.stop()}>
                <Square size={14} />
                Stop
              </button>
              <button className="secondary" onClick={pause}>
                {state === "paused" ? <Play size={14} /> : <Pause size={14} />}{" "}
                {state === "paused" ? "Resume" : "Pause"}
              </button>
            </>
          )}
          <button
            className="secondary"
            onClick={() => input.current?.click()}
            disabled={busy || state !== "idle"}
          >
            <Upload size={15} />
            Upload audio
          </button>
        </div>
        <input
          ref={input}
          type="file"
          accept=".wav,.mp3,.ogg,.webm,.m4a,.flac"
          aria-label="Upload audio file"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void upload(file);
            e.target.value = "";
          }}
        />
        {busy && <Busy label="Decoding and inspecting audio" />}
      </div>
      <ErrorBox error={error} />
      {media && (
        <div className="audio-preview">
          <div className="split-label">
            <span>Source recording</span>
            <span>
              {media.duration_seconds.toFixed(2)} s · {media.sample_rate / 1000}{" "}
              kHz · mono
            </span>
          </div>
          <Waveform data={media.waveform} />
          <audio controls src={media.url} />
          {media.silent && (
            <p className="warning">
              This recording appears silent. Speech recognition may fail.
            </p>
          )}
          {media.clipped_fraction > 0.01 && (
            <p className="warning">
              Input clipping detected. Reduce your microphone gain.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
