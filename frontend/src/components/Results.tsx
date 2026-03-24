
import { Download, CheckCircle2, AlertTriangle } from "lucide-react";
import type { Result } from "../types";
import { MetricGrid } from "./ui";
import { Waveform, Spectrogram } from "./AudioInput";
export function Results({
  result,
  compact = false,
}: {
  result: Result;
  compact?: boolean;
}) {
  return (
    <div className="results"><div
        className={
          "result-status " +
          (result.recovery_status === "recovered" ? "success" : "failure")
        }
      >
        {result.recovery_status === "recovered" ? (
          <CheckCircle2 size={19} />
        ) : (
          <AlertTriangle size={19} />
        )}
        <div>
          <strong>
            {result.recovery_status === "recovered"
              ? "Payload recovered with valid CRCs"
              : "Payload recovery failed"}
          </strong>
          <p>{result.failure || result.provider}</p>
        </div>
      </div>{result.reconstruction_error && (
        <div className="error" role="alert">
          Audio reconstruction failed: {result.reconstruction_error}
        </div>
      )}{result.recovered_text !== null && (
        <div className="transcript">
          <span className="eyebrow">Recovered receiver text</span>
          <p lang={result.config.language}>{result.recovered_text}</p>
        </div>
      )}{result.receiver && (
        <>
          <Waveform data={result.receiver.waveform} />
          <audio controls src={result.receiver.url} />
          <a className="text-link" href={result.receiver.url} download>
            <Download size={14} />
            Download receiver audio
          </a>
          {!compact && <Spectrogram media={result.receiver} />}
        </>
      )}<MetricGrid metrics={result.metrics} /><div className="packet-strip" aria-label="Packet delivery results">
        {result.packets.slice(0, 180).map((p) => (
          <i
            key={p.sequence}
            className={p.status}
            title={`Packet ${p.sequence}: ${p.status}; bit errors ${p.bit_errors ?? "not comparable"}`}
          />
        ))}
      </div><p className="muted small">
        {result.packets.length} packets · green: CRC valid · red: corrupt ·
        amber: erased
      </p>{result.metrics.budget_exceeded && (
        <p className="warning">
          Measured wire bits per speech second exceed the configured budget.
        </p>
      )}</div>
  );
}