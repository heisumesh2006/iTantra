import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ScatterChart,
  Scatter,
} from "recharts";
import { FlaskConical, RotateCcw, Download } from "lucide-react";
import { api, baseline, message } from "../api";
import type { Channel, Sweep } from "../types";
import { PageTitle, Panel, Busy, ErrorBox, Empty } from "../components/ui";
import { ChannelControls } from "../components/ChannelControls";
export default function ChannelLab() {
  const [config, setConfig] = useState<Channel>({ ...baseline });
  const [result, setResult] = useState<Sweep | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trials, setTrials] = useState(24);
  async function run() {
    setBusy(true);
    setError(null);
    try {
      setResult(
        await api<Sweep>("/channels/simulate", {
          method: "POST",
          body: JSON.stringify({
            config,
            snr_values: [-4, -2, 0, 2, 4, 6, 8, 10, 12, 16, 20],
            trials,
          }),
        }),
      );
    } catch (e) {
      setError(message(e));
    } finally {
      setBusy(false);
    }
  }
  function download() {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify({ config, result }, null, 2)], {
        type: "application/json",
      }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = "itantra-channel-sweep.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return (
    <>
      <PageTitle
        tag="RESEARCH / DIGITAL RADIO"
        title="Channel Simulation Lab"
        description="Explore symbol decisions, bit errors and packet integrity with reproducible numerical experiments."
        action={<span className="badge">Es/N0 · not Eb/N0</span>}
      />
      <ErrorBox error={error} />
      <div className="lab-grid">
        <Panel title="Experiment configuration" eyebrow="CONTROLLED CONDITIONS">
          <ChannelControls value={config} onChange={setConfig} />
          <label>
            Trials at each Es/N0
            <input
              type="number"
              value={trials}
              min={1}
              max={100}
              onChange={(e) => setTrials(+e.target.value)}
            />
          </label>
          <p className="muted small">
            Each trial transmits a seeded 1,024-byte payload. BER excludes
            erased packets. Rayleigh uses independent flat fading per symbol and
            perfect CSI.
          </p>
          <button className="full" disabled={busy} onClick={() => void run()}>
            {busy ? (
              <Busy label="Calculating sweep" />
            ) : (
              <>
                <FlaskConical size={17} />
                Run SNR sweep
              </>
            )}
          </button>
          <button
            className="secondary full"
            onClick={() => setConfig({ ...baseline })}
          >
            <RotateCcw size={14} />
            Reset baseline
          </button>
        </Panel>
        <div className="chart-stack">
          <Panel
            title="Bit error rate"
            eyebrow="EMPIRICAL VS. ANALYTICAL"
            action={
              result && (
                <button className="text-link" onClick={download}>
                  <Download size={14} />
                  Data
                </button>
              )
            }
          >
            {result ? (
              <>
                <div className="chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.points}>
                      <CartesianGrid stroke="#253044" strokeDasharray="3 3" />
                      <XAxis
                        dataKey="snr_db"
                        stroke="#8793a8"
                        label={{
                          value: "Es/N0 (dB)",
                          position: "insideBottom",
                          offset: -5,
                        }}
                      />
                      <YAxis stroke="#8793a8" domain={[0, "auto"]} />
                      <Tooltip
                        contentStyle={{
                          background: "#111b2a",
                          border: "1px solid #334155",
                        }}
                      />
                      <Legend />
                      <Line
                        name="Measured BER"
                        dataKey="ber"
                        stroke="#59dfd6"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                      <Line
                        name="Uncoded AWGN reference"
                        dataKey="theoretical_ber"
                        stroke="#9c87ff"
                        strokeDasharray="4 4"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p className="muted small">
                  The analytical curve appears only for matching uncoded AWGN
                  assumptions. A zero measured BER is a finite-sample
                  observation.
                </p>
              </>
            ) : (
              <Empty>
                Run a sweep to generate measured points. No preloaded results.
              </Empty>
            )}
          </Panel>
          <div className="two-col">
            <Panel title="Packet recovery" eyebrow="CRC VALIDATION">
              {result ? (
                <div className="chart short">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={result.points}>
                      <CartesianGrid stroke="#253044" />
                      <XAxis dataKey="snr_db" stroke="#8793a8" />
                      <YAxis domain={[0, 1]} stroke="#8793a8" />
                      <Tooltip contentStyle={{ background: "#111b2a" }} />
                      <Legend />
                      <Line
                        name="Packet error rate"
                        dataKey="packet_error_rate"
                        stroke="#f49c78"
                        dot={false}
                      />
                      <Line
                        name="Full recovery rate"
                        dataKey="recovery_rate"
                        stroke="#59dfd6"
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <Empty>Measured packet outcomes will appear here.</Empty>
              )}
            </Panel>
            <Panel
              title="Received constellation"
              eyebrow="FINAL SNR / FINAL TRIAL"
            >
              {result ? (
                <div className="chart short">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid stroke="#253044" />
                      <XAxis
                        type="number"
                        dataKey="i"
                        name="In-phase"
                        stroke="#8793a8"
                      />
                      <YAxis
                        type="number"
                        dataKey="q"
                        name="Quadrature"
                        stroke="#8793a8"
                      />
                      <Tooltip contentStyle={{ background: "#111b2a" }} />
                      <Scatter data={result.constellation} fill="#9c87ff" />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <Empty>Actual received complex symbols, up to 256.</Empty>
              )}
            </Panel>
          </div>
        </div>
      </div>
    </>
  );
}
