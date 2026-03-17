export type Mode = "conventional" | "neural" | "semantic" | "adaptive";
export type Channel = {
  modulation: "BPSK" | "QPSK";
  channel: "ideal" | "awgn" | "rayleigh";
  snr_db: number;
  packet_size: number;
  repetition: 1 | 3;
  erasure_rate: number;
  bit_flip_rate: number;
  seed: number;
  symbol_rate: number;
};
export type Language = {
  code: string;
  name: string;
  native: string;
  status: string;
  stt_installed: boolean;
  tts_installed: boolean;
  stt_verified: boolean;
  tts_verified: boolean;
  tts_model: string;
  stt_model: string;
};
export type Capabilities = {
  simulation_mode: boolean;
  languages: Language[];
  neural: {
    installed: boolean;
    verified: boolean;
    model: string;
    bandwidths: number[];
  };
  stt: { provider: string; model: string };
  privacy: string;
};
export type Media = {
  id: string;
  url: string;
  duration_seconds: number;
  sample_rate: number;
  samples: number;
  channels: number;
  waveform: number[];
  silent: boolean;
  clipped_fraction: number;
  spectrogram: { values: number[][]; frequencies: number[]; times: number[] };
};
export type Metrics = Record<string, number | boolean | null>;
export type TransmissionConfig = {
  media_id?: string;
  mode: Mode;
  language: string;
  text?: string;
  reference?: string;
  bandwidth_kbps: number;
  budget_kbps: number;
  objective: "meaning" | "waveform";
  target_latency_ms: number;
  channel_config: Channel;
};
export type Result = {
  mode: Mode;
  provider: string;
  source: Media | null;
  receiver: Media | null;
  sender_text: string | null;
  recovered_text: string | null;
  semantic_input: string | null;
  recovery_status: string;
  reconstruction_error?: string | null;
  reconstruction_status?: string;
  failure: string | null;
  metrics: Metrics;
  timing: Record<string, number>;
  config: TransmissionConfig;
  packets: { sequence: number; status: string; bit_errors: number | null }[];
  constellation: {
    i: number;
    q: number;
    equalized_i: number;
    equalized_q: number;
  }[];
  decision: { mode: Mode; reason: string; tradeoffs: string[] } | null;
  stt: { model: string; processing_ms: number } | null;
  tts: { model: string; processing_ms: number } | null;
};
export type Job = {
  id: string;
  created_at: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  config: TransmissionConfig;
  result: Result | null;
  error: string | null;
  stages: { name: string; timestamp: string; detail: unknown }[];
};
export type Sweep = {
  points: {
    snr_db: number;
    ber: number | null;
    packet_error_rate: number;
    recovery_rate: number;
    theoretical_ber: number | null;
  }[];
  constellation: Result["constellation"];
  snr_definition: string;
};