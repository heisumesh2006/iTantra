import type { ReactNode } from "react";
import { ArrowUpRight, LoaderCircle } from "lucide-react";
import type { Metrics } from "../types";
export function Panel({
  children,
  title,
  eyebrow,
  action,
  className = "",
}: {
  children: ReactNode;
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section className={"panel " + className}>
      {title && (
        <div className="panel-heading">
          <div>
            {eyebrow && <span className="eyebrow">{eyebrow}</span>}
            <h2>{title}</h2>
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
export function PageTitle({
  tag,
  title,
  description,
  action,
}: {
  tag: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <header className="page-title">
      <div>
        <span className="eyebrow">{tag}</span>
        <h1>
          {title}
          <span className="title-dot">.</span>
        </h1>
        <p>{description}</p>
      </div>
      {action}
    </header>
  );
}
export function ErrorBox({ error }: { error: string | null }) {
  return error ? (
    <div className="error" role="alert">
      {error}
    </div>
  ) : null;
}
export function Empty({ children }: { children: ReactNode }) {
  return (
    <div className="empty">
      <ArrowUpRight size={22} />
      <p>{children}</p>
    </div>
  );
}
export function Busy({ label = "Processing" }: { label?: string }) {
  return (
    <span className="busy">
      <LoaderCircle size={16} />
      {label}
    </span>
  );
}
export function format(value: unknown, digits = 2) {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toLocaleString(undefined, { maximumFractionDigits: digits })
    : "Not measured";
}
const fields = [
  ["payload_bytes", "Payload", "bytes"],
  ["effective_link_bitrate_bps", "Bits / speech second", "bps"],
  ["raw_ber", "Raw bit error rate", ""],
  ["packet_delivery_rate", "Packet delivery", "ratio"],
  ["total_ms", "Compute latency", "ms"],
  ["simulated_link_seconds", "Simulated airtime", "s"],
  ["compression_ratio", "PCM / payload", "×"],
  ["si_sdr_db", "Waveform SI-SDR", "dB"],
];
export function MetricGrid({ metrics }: { metrics: Metrics }) {
  return (
    <div className="metric-grid">
      {fields.map(([key, label, unit]) => (
        <div className="metric" key={key}>
          <span>{label}</span>
          <strong>
            {format(metrics[key], key === "raw_ber" ? 6 : 2)}{" "}
            <small>{typeof metrics[key] === "number" ? unit : ""}</small>
          </strong>
        </div>
      ))}
    </div>
  );
}
