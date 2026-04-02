import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trash2, ArrowUpRight, RefreshCw } from "lucide-react";
import { api, message } from "../api";
import type { Job, Experiment } from "../types";
import { PageTitle, Panel, ErrorBox, Empty, format } from "../components/ui";
export default function History() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState<string | null>(null);
  async function load() {
    setError(null);
    try {
      const [a, b] = await Promise.all([
        api<Job[]>("/transmissions"),
        api<Experiment[]>("/experiments"),
      ]);
      setJobs(a);
      setExperiments(b);
    } catch (e) {
      setError(message(e));
    }
  }
  useEffect(() => {
    void load();
  }, []);
  async function remove(id: string) {
    if (
      !window.confirm(
        "Delete this session and its source / receiver audio? Other sessions sharing the same source may lose playback.",
      )
    )
      return;
    try {
      await api("/transmissions/" + id, { method: "DELETE" });
      await load();
    } catch (e) {
      setError(message(e));
    }
  }
  return (
    <>
      <PageTitle
        tag="RECORDS / LOCAL SQLITE"
        title="Experiment History"
        description="Real sessions only. Configuration and results persist locally; audio expires after 24 hours by default."
        action={
          <button className="secondary" onClick={() => void load()}>
            <RefreshCw size={16} />
            Refresh
          </button>
        }
      />
      <ErrorBox error={error} />
      <Panel
        title="Transmission sessions"
        action={
          <input
            className="filter"
            placeholder="Filter mode, language, status"
            aria-label="Filter sessions"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        }
      >
        <div className="table-wrap">
          {jobs.length ? (
            <table>
              <thead>
                <tr>
                  <th>Session / time</th>
                  <th>Mode</th>
                  <th>Language</th>
                  <th>Channel</th>
                  <th>Es/N0</th>
                  <th>Status</th>
                  <th>Compute</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs
                  .filter((j) =>
                    `${j.config.mode} ${j.config.language} ${j.status} ${j.result?.recovery_status}`.includes(
                      filter.toLowerCase(),
                    ),
                  )
                  .map((j) => (
                    <tr key={j.id}>
                      <td>
                        <b>{j.id.slice(0, 8)}</b>
                        <small>{new Date(j.created_at).toLocaleString()}</small>
                      </td>
                      <td>{j.result?.mode || j.config.mode}</td>
                      <td>{j.config.language}</td>
                      <td>{j.config.channel_config.channel}</td>
                      <td>{j.config.channel_config.snr_db} dB</td>
                      <td>
                        <span
                          className={
                            "status-chip " +
                            (j.result?.recovery_status === "recovered"
                              ? "success"
                              : "")
                          }
                        >
                          {j.result?.recovery_status || j.status}
                        </span>
                      </td>
                      <td>{format(j.result?.metrics.total_ms)} ms</td>
                      <td>
                        <div className="button-row">
                          <Link
                            aria-label="Open session"
                            to={"/studio?id=" + j.id}
                          >
                            <ArrowUpRight size={17} />
                          </Link>
                          <a
                            href={
                              "/api/v1/exports/transmissions/" +
                              j.id +
                              "?format=json"
                            }
                          >
                            JSON
                          </a>
                          <button
                            className="icon-button"
                            disabled={["queued", "running"].includes(j.status)}
                            onClick={() => void remove(j.id)}
                            aria-label="Delete session"
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          ) : (
            <Empty>No saved transmissions. Start in the studio.</Empty>
          )}
        </div>
      </Panel>
      <Panel title="Batch experiments" eyebrow="SAVED CONFIGURATIONS">
        {experiments.length ? (
          <div className="experiment-list">
            {experiments.map((j) => (
              <div key={j.id}>
                <b>{j.id.slice(0, 8)}</b>
                <span>{new Date(j.created_at).toLocaleString()}</span>
                <span>
                  {j.status} · {j.result?.runs.length ?? 0} trials
                </span>
                <a
                  href={"/api/v1/exports/experiments/" + j.id + "?format=json"}
                >
                  JSON
                </a>
                <a href={"/api/v1/exports/experiments/" + j.id + "?format=csv"}>
                  CSV
                </a>
              </div>
            ))}
          </div>
        ) : (
          <Empty>
            Batch comparisons are available in Performance Analytics.
          </Empty>
        )}
      </Panel>
    </>
  );
}
